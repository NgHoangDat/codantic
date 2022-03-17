from typing import *

from .base import Annotation, CocoDataset

__all__ = ["CaptionAnnotation", "CaptionCocoDataset"]


class CaptionAnnotation(Annotation):
    caption: str


class CaptionCocoDataset(CocoDataset):
    annotations: List[CaptionAnnotation] = []
