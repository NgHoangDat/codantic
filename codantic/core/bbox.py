from enum import Enum
from typing import *

from mousse.functional import compose

__all__ = ["BBoxType", "BBox", "convert_bbox", "bbox_converter", "bbox_fields"]

BBox = Sequence[float]


class BBoxType(str, Enum):
    ltrb: str = "ltrb"  # (left, top, right, bottom)
    ltwh: str = "ltwh"  # (left, top, width, height)
    xywh: str = "xywh"  # (x center, y center, width, height)


class BBoxConverterNotFoundException(Exception):
    def __init__(self, source: BBoxType, target: BBoxType) -> None:
        super().__init__(
            (
                f"No conversion found between {source.value} and {target.value}. ",
                f"Please implement function {source.value}2{target.value} and add by decorator `bbox_converter`",
            )
        )


bbox_fields = {
    BBoxType.ltrb: ("left", "top", "right", "bottom"),
    BBoxType.ltwh: ("left", "top", "width", "height"),
    BBoxType.xywh: ("x", "y", "width", "height"),
}


bbox_converters = {}


def convert_bbox(bbox: BBox, source: BBoxType, target: BBoxType) -> BBox:
    if source == target:
        return bbox

    has_converter = False

    converter = f"{source.value}2{target.value}"
    if converter not in bbox_converters:
        source_to_ltrb = f"{source.value}2ltrb"
        ltrb_to_target = f"ltrb2{target.value}"

        if source_to_ltrb in bbox_converters and ltrb_to_target in bbox_converters:
            source_to_ltrb = bbox_converters[source_to_ltrb]
            ltrb_to_target = bbox_converters[ltrb_to_target]
            converter = compose(ltrb_to_target, source_to_ltrb)
            has_converter = True
    else:
        converter = bbox_converters[converter]
        has_converter = True

    if not has_converter:
        raise BBoxConverterNotFoundException(source, target)

    return converter(bbox)


def bbox_converter(func: Callable[[BBox], BBox]):
    bbox_converters[func.__name__] = func
    return func


@bbox_converter
def ltrb2ltwh(bbox: BBox) -> BBox:
    assert len(bbox) >= 4, "Number of elements for a bbox must be greater or equal 4"
    return [
        bbox[0],
        bbox[1],
        bbox[2] - bbox[0],
        bbox[3] - bbox[1],
    ]


@bbox_converter
def ltwh2ltrb(bbox: BBox) -> BBox:
    assert len(bbox) >= 4, "Number of elements for a bbox must be greater or equal 4"
    return [
        bbox[0],
        bbox[1],
        bbox[2] + bbox[0],
        bbox[3] + bbox[1],
    ]


@bbox_converter
def ltrb2xywh(bbox: BBox) -> BBox:
    assert len(bbox) >= 4, "Number of elements for a bbox must be greater or equal 4"
    return [
        (bbox[0] + bbox[2]) / 2,
        (bbox[1] + bbox[3]) / 2,
        bbox[2] - bbox[0],
        bbox[3] - bbox[1],
    ]


@bbox_converter
def xywh2ltrb(bbox: BBox) -> BBox:
    assert len(bbox) >= 4, "Number of elements for a bbox must be greater or equal 4"
    return [
        bbox[0] - bbox[2] / 2,
        bbox[1] - bbox[3] / 2,
        bbox[0] + bbox[2] / 2,
        bbox[1] + bbox[3] / 2,
    ]
