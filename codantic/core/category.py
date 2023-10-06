from mousse import Dataclass, Field

__all__ = ["Category"]


class Category(Dataclass, dynamic=True):
    category_id: int = Field(alias="id")
    name: str = None
    super_category: str = Field(alias="supercategory")
