from typing import *

from .object_detection import ODAnnotation, ODCocoDataset


__all__ = ["FaceAnnotation", "FaceCocoDataset"]


class FaceAnnotation(ODAnnotation):
    keypoints: Sequence[float] = []
    landmarks: Sequence[Tuple[float, float]] = []


class FaceCocoDataset(ODCocoDataset):
    annotations: List[FaceAnnotation] = []
