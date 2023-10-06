from collections import defaultdict
from typing import *

from mousse import Dataclass, Field

__all__ = ["CocoDataset", "Image", "Annotation", "Category"]


class Info(Dataclass):
    year: str = None
    version: str = None
    description: str = None
    contributor: str = None
    url: str = None
    date_created: str = None


class License(Dataclass):
    license_id: int = Field(..., alias="id")
    url: str = None
    name: str = None


class Image(Dataclass):
    image_id: int = Field(alias="id")
    file_name: str = None
    width: int = None
    height: int = None
    license_id: int = Field(default=None, alias="license")
    date_captured: str = None
    attributes: Dict[str, Any] = {}


class Annotation(Dataclass):
    annotation_id: int = Field(None, alias="id")
    image_id: int = None
    category_id: int = None
    keypoints: Sequence[float] = []
    attributes: Dict[str, Any] = {}


class Category(Dataclass):
    category_id: int = Field(alias="id")
    name: str = None
    super_category: str = Field(default=None, alias="supercategory")


class CocoDataset(Dataclass):
    info: Info = Info()
    licenses: List[License] = []
    images: List[Image] = []
    annotations: List[Annotation] = []
    categories: List[Category] = []

    def get_images_info(self) -> Dict[int, Image]:
        """_summary_

        Returns:
            Dict[int, Image]: Mapping from image_id to Image object
        """
        images = {}
        for image_info in self.images:
            images[image_info.image_id] = image_info

        return images

    def get_categories_info(self) -> Dict[int, Category]:
        """_summary_

        Returns:
            Dict[int, Category]: Mapping from category_id to Category object
        """
        categories = {}
        for category_info in self.categories:
            categories[category_info.category_id] = category_info
        return categories

    def get_annotation_groups(
        self, category_id: Optional[int] = None
    ) -> Dict[int, List[Annotation]]:
        """_summary_

        Args:
            category_id (Optional[int], optional): category to select. Defaults to None.

        Returns:
            Dict[int, List[Annotation]]: Mapping from image_id to list of annotations, filtered by category if provided
        """
        annotation_groups = defaultdict(list)
        for annotation in self.annotations:
            if category_id is not None:
                if annotation.category_id == category_id:
                    annotation_groups[annotation.image_id].append(annotation)
            else:
                annotation_groups[annotation.image_id].append(annotation)

        return dict(annotation_groups)
