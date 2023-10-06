from collections import defaultdict
from typing import *

import pandas as pd
from mousse import Dataclass, Field, Registry
from mousse.types import get_args, get_fields_info

from .annotation import Annotation
from .category import Category
from .image import Image
from .video import Video

__all__ = ["Dataset", "Video", "Image", "Annotation", "Category", "dataset_registry"]

dataset_registry = Registry.get("dataset")


class DatasetInfo(Dataclass, dynamic=True):
    version: str = None
    description: str = None
    url: str = None
    date_created: str = None


@dataset_registry.register()
class Dataset(Dataclass, dynamic=True):
    info: DatasetInfo = DatasetInfo()
    videos: List[Video] = []
    images: List[Image] = []
    annotations: List[Annotation] = []
    categories: List[Category] = []

    def groupby(self, *keys: List[str]) -> Dict[Hashable, "Dataset"]:
        groups = defaultdict(Dataset)
        for annotation in self.annotations:
            group = tuple(getattr(annotation, key, Ellipsis) for key in keys)
            groups[group].annotations.append(annotation)
            
        videos = {}
        for video in self.videos:
            videos[video.video_id] = video
            
        images = {}
        for image in self.images:
            images[(image.video_id, image.image_id)] = image
                    
        groups: Dict[Hashable, Dataset] = dict(groups)
        for group, group_dataset in groups.items():
            group_dataset.info = self.info
            for annotation in group_dataset.annotations:
                video = videos[annotation.video_id]
                image = images[(annotation.video_id, annotation.image_id)]
            
        return groups

    def get_annotation_groups(
        self, category_id: Optional[int] = None
    ) -> Dict[int, List[Annotation]]:
        annotation_groups = defaultdict(list)
        for annotation in self.annotations:
            if category_id is not None:
                if annotation.category_id == category_id:
                    annotation_groups[annotation.image_id].append(annotation)
            else:
                annotation_groups[annotation.image_id].append(annotation)

        return dict(annotation_groups)

    @classmethod
    def get_annotation_type(cls) -> Type[Annotation]:
        fields = get_fields_info(cls)
        annotation_type, *_ = get_args(fields["annotations"].annotation)
        return annotation_type

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> "Dataset":
        """[summary]

        Args:
            df (pd.DataFrame): [description]
        """
        dataset: Dataset = cls()

        images: Dict[Tuple[int, str], Image] = {}
        categories: Dict[str, Category] = {}

        df.fillna(value="none", inplace=True)
        annotation_type = cls.get_annotation_type()

        for item in df.itertuples():
            video_name = getattr(item, "video_name", "")
            image_id = (item.image_id, video_name)

            if image_id not in images:
                image = Image(image_id=item.image_id, video_name=video_name)
                images[image_id] = image
                dataset.images.append(image)

            if item.category_name not in categories:
                category = Category(
                    category_id=len(categories), name=item.category_name
                )
                categories[item.category_name] = category
                dataset.categories.append(category)

            image = images[image_id]
            category = categories[item.category_name]

            annotation = annotation_type(
                annotation_id=item.annotation_id,
                image_id=image.image_id,
                video_name=image.video_name,
            )
            annotation.category_id = category.category_id
            annotation.load(item._asdict())

            dataset.annotations.append(annotation)

        return dataset

    def to_df(self, columns: Sequence[str] = None) -> pd.DataFrame:
        """[summary]

        Returns:
            pd.DataFrame: [description]
        """
        images_id = tuple(image.image_id for image in self.images)
        annotations = [
            annotation
            for annotation in self.annotations
            if annotation.image_id in images_id
        ]

        annotations.sort(
            key=lambda annotation: (
                images_id.index(annotation.image_id),
                annotation.annotation_id,
            )
        )

        categories = {
            category.category_id: category.name for category in self.categories
        }

        data = []
        for annotation in annotations:
            item = {
                "image_id": annotation.image_id,
                "annotation_id": annotation.annotation_id,
                "category_name": categories.get(annotation.category_id),
            }

            item.update(annotation.dump())
            data.append(item)

        if columns is not None:
            return pd.DataFrame(data=data, columns=columns)

        return pd.DataFrame(data=data)
