from enum import Enum
from typing import *

import numpy as np
import pandas as pd
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval as BaseCOCOEval

from mousse import asdict

from codantic.models import Category
from codantic.models.object_detection import ODCocoDataset

__all__ = ["ODCocoEvaluator", "IOUType"]


class IOUType(Enum):
    bbox = "bbox"


class ODCocoEvaluator(BaseCOCOEval):
    def __init__(
        self,
        gold_dataset: ODCocoDataset,
        pred_dataset: ODCocoDataset,
        iou_type: IOUType = IOUType.bbox,
    ):
        align_categories(gold_dataset, pred_dataset)

        gold_coco = COCO()
        gold_coco.dataset = asdict(gold_dataset, by_alias=True)
        gold_coco.createIndex()

        pred_coco = COCO()
        pred_coco.dataset = asdict(pred_dataset, by_alias=True)
        pred_coco.createIndex()

        super().__init__(cocoGt=gold_coco, cocoDt=pred_coco, iouType=iou_type.value)
        self.classes = tuple(category.name for category in gold_dataset.categories)

    def _load_classes(self, x: int):
        return self.classes[int(x)]

    def summarize(self) -> pd.DataFrame:
        """
        Compute and display summary metrics for evaluation results.
        Note this functin can *only* be applied on the default parameter setting
        """

        def _summarize(
            ap: int = 1, iouThr: float = None, areaRng: str = "all", maxDets: int = 100
        ):
            p = self.params

            aind = [i for i, aRng in enumerate(p.areaRngLbl) if aRng == areaRng]
            mind = [i for i, mDet in enumerate(p.maxDets) if mDet == maxDets]
            if ap == 1:
                s = self.eval["precision"]
                if iouThr is not None:
                    t = np.where(iouThr == p.iouThrs)[0]
                    s = s[t]
                s = s[:, :, :, aind, mind]
            else:
                # dimension of recall: [TxKxAxM]
                s = self.eval["recall"]
                if iouThr is not None:
                    t = np.where(iouThr == p.iouThrs)[0]
                    s = s[t]
                s = s[:, :, aind, mind]
            if len(s[s > -1]) == 0:
                mean_s = -1
            else:
                mean_s = []

                # caculate AP(average precision) for each category
                num_classes = len(self.params.catIds)

                if ap == 1:
                    for i in range(0, num_classes):
                        mean_s.append(np.mean(s[:, :, i, :]))
                else:
                    for i in range(0, num_classes):
                        mean_s.append(np.mean(s[:, i, :]))

            return mean_s

        def _summarizeDets():
            stats = np.zeros((8, len(self.classes)))
            stats[0] = list(range(len(self.classes)))
            stats[1] = np.full((len(self.classes),), len(self.params.imgIds))
            stats[2] = _summarize(1)
            stats[3] = _summarize(1, iouThr=0.5, maxDets=self.params.maxDets[2])
            stats[4] = _summarize(
                1, iouThr=0.5, areaRng="small", maxDets=self.params.maxDets[2]
            )
            stats[5] = _summarize(
                1, iouThr=0.5, areaRng="medium", maxDets=self.params.maxDets[2]
            )
            stats[6] = _summarize(
                1, iouThr=0.5, areaRng="large", maxDets=self.params.maxDets[2]
            )
            stats[7] = _summarize(0, iouThr=0.5, maxDets=self.params.maxDets[2])
            return stats

        if not self.eval:
            raise Exception("Please run accumulate() first")

        iouType = self.params.iouType
        if iouType == "segm" or iouType == "bbox":
            summarize = _summarizeDets
        else:
            raise ValueError(iouType)

        self.stats = summarize()
        self.stats = np.array(self.stats)
        self.stats = np.transpose(self.stats)

        pd_stat = pd.DataFrame(self.stats)
        pd_stat.columns = [
            "classes",
            "images",
            "mAP@.5:@.95",
            "mAP@.5",
            "mAP@.5(small)",
            "mAP@.5(medium)",
            "mAP@.5(large)",
            "mAR@.5:.95",
        ]
        pd_stat["classes"] = pd_stat["classes"].apply(self._load_classes)
        return pd_stat


def align_categories(gold_dataset: ODCocoDataset, pred_dataset: ODCocoDataset):
    categories = set()

    gold_categories = {}
    for category in gold_dataset.categories:
        name = category.name.strip()
        gold_categories[category.category_id] = name
        categories.add(name)

    pred_categories = {}
    for category in pred_dataset.categories:
        name = category.name.strip()
        pred_categories[category.category_id] = category.name
        categories.add(name)

    categories = list(categories)
    categories.sort()
    aligned_categories = [
        Category(id=categories.index(category), name=category)
        for category in categories
    ]

    gold_dataset.categories = aligned_categories
    pred_dataset.categories = aligned_categories

    for annotation in gold_dataset.annotations:
        annotation.category_id = categories.index(
            gold_categories[annotation.category_id]
        )
        annotation.attributes = {}

    for annotation in pred_dataset.annotations:
        annotation.category_id = categories.index(
            pred_categories[annotation.category_id]
        )
