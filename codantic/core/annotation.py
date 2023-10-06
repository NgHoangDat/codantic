from typing import *

from mousse import Dataclass, Field

from .bbox import BBox, bbox_fields, convert_bbox, BBoxType


__all__ = ["Annotation"]


class Annotation(Dataclass, dynamic=True):
    annotation_id: int = Field(alias="id")
    
    image_id: int
    video_id: int

    category_id: int = -1
    bbox: BBox = None

    def __build__(self):
        if self.bbox is None:
            for btype, fields in bbox_fields.items():
                if all(hasattr(self, field) for field in fields):
                    self.bbox = convert_bbox(
                        tuple(getattr(self, field) for field in fields),
                        btype,
                        BBoxType.ltwh,
                    )
