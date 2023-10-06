from typing import *

from mousse import Dataclass, Field

__all__ = ["Image"]


class Image(Dataclass, dynamic=True):
    image_id: int = Field(alias="id")
    video_id: int
    file_name: str = None
    file_url: str = None
    width: int = None
    height: int = None
    date_created: str = None
    category_id: int = -1
