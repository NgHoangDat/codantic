from functools import wraps
from typing import *

from pydantic import BaseModel, PrivateAttr


class ExtensibleModel(BaseModel):

    __data: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def __getitem__(self, key: Hashable) -> Any:
        return self.__data[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self.__data[key] = value

    def __contains__(self, key: Hashable) -> bool:
        return key in self.__data

    @classmethod
    def parse_obj(cls, data: Dict[str, Any]):
        instance = super().parse_obj(data)
        data.update(instance.dict(by_alias=True))

        for key, val in data.items():
            instance[key] = val

        return instance

    @wraps(BaseModel.dict)
    def dict(self, **kwargs):
        data = self.__data.copy()
        data.update(super().dict(**kwargs))
        return data
