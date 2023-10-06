from mousse import Dataclass, Field

__all__ = ["Video"]


class Video(Dataclass, dynamic=True):
    video_id: int = Field(alias="id")
    name: str
    num_frame: int
    url: str = None
    fps: int = -1
    category_id: int = -1
