from typing import *

from pydantic import BaseModel, Field
from .base import Annotation, CocoDataset

__all__ = ["BBox", "ODAnnotation", "ODCocoDataset"]


class BBox(BaseModel):
    left: float
    top: float
    bottom: float
    right: float

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def area(self):
        return (self.right - self.left) * (self.bottom - self.top)

    def ltrb(self, dtype: Type = float):
        return dtype(self.left), dtype(self.top), dtype(self.right), dtype(self.bottom)

    def ltwh(self, dtype: Type = float):
        return dtype(self.left), dtype(self.top), dtype(self.width), dtype(self.height)

    def __contains__(self, other: "BBox") -> bool:
        return (
            self.left <= other.left
            and self.right >= other.right
            and self.top <= other.top
            and self.bottom >= other.bottom
        )

    def __lt__(self, other: "BBox") -> bool:
        if self.left < other.left:
            return True

        if self.left == other.left:
            return self.top < other.top

        return False

    def __le__(self, other: "BBox") -> bool:
        if self.left < other.left:
            return True

        if self.left == other.left:
            return self.top <= other.top

        return False

    def __gt__(self, other: "BBox") -> bool:
        return not other <= self

    def __ge__(self, other: "BBox") -> bool:
        return not other < self

    def __eq__(self, other: "BBox") -> bool:
        return (
            self.left == other.left
            and self.right == other.right
            and self.top == other.top
            and self.bottom == other.bottom
        )

    def __and__(self, other: "BBox") -> Optional["BBox"]:
        if (
            self.left <= other.right
            or self.right <= other.left
            or self.bottom >= other.top
            or self.top <= other.bottom
        ):
            return None

        left = max(self.left, other.left)
        top = max(self.top, other.top)
        right = min(self.right, other.right)
        bottom = min(self.bottom, other.bottom)

        return BBox(left=left, top=top, right=right, bottom=bottom)


class ODAnnotation(Annotation):
    bbox: Tuple[float, float, float, float]
    area: float = 0
    score: float = 1

    def get_bbox(self) -> BBox:
        x_min, y_min, width, height = self.bbox
        return BBox(left=x_min, top=y_min, right=x_min + width, bottom=y_min + height)


class ODCocoDataset(CocoDataset):
    annotations: List[ODAnnotation] = []
