from collections import defaultdict
from turtle import right, width
from typing import *

from pydantic import BaseModel, Field

from .common import ExtensibleModel

__all__ = ["CocoDataset", "Image", "ODAnnotation", "Category"]


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


class DatasetInfo(ExtensibleModel):
    year: str = None
    version: str = None
    description: str = None
    contributor: str = None
    url: str = None
    date_created: str = None


class ODAnnotation(ExtensibleModel):
    annotation_id: int = Field(None, alias="id")
    image_id: int = 0
    category_id: int = 0

    area: float = 0

    bbox: Sequence[float] = tuple()
    keypoints: Sequence[float] = []
    landmarks: Sequence[Tuple[float, float]] = []

    attributes: Dict[str, Any] = {}
    score: float = 1

    def get_bbox(self) -> BBox:
        x_min, y_min, width, height = self.bbox
        return BBox(left=x_min, top=y_min, right=x_min + width, bottom=y_min + height)


class Image(ExtensibleModel):
    image_id: int = Field(alias="id")
    file_name: str = None
    width: int = None
    height: int = None
    license: str = None
    flickr_url: str = None
    coco_url: str = None
    date_captured: str = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class Category(ExtensibleModel):
    category_id: int = Field(alias="id")
    name: str = None
    super_category: str = Field(default=None, alias="supercategory")


class CocoDataset(ExtensibleModel):
    info: DatasetInfo = DatasetInfo()
    images: List[Image] = []
    annotations: List[ODAnnotation] = []
    categories: List[Category] = []

    def get_images_info(self) -> Dict[int, Image]:
        images = {}
        for image_info in self.images:
            images[image_info.image_id] = image_info

        return images

    def get_annotation_groups(
        self, category_id: Optional[int] = None
    ) -> Dict[int, List[ODAnnotation]]:
        annotation_groups = defaultdict(list)
        for annotation in self.annotations:
            if category_id is not None:
                if annotation.category_id == category_id:
                    annotation_groups[annotation.image_id].append(annotation)
            else:
                annotation_groups[annotation.image_id].append(annotation)

        return dict(annotation_groups)
