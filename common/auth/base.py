from abc import ABC, abstractmethod
from typing import Type, TypeVar, Dict, Any

from dataclasses import dataclass, fields


T = TypeVar("T")


class Authentication(ABC):

    @dataclass
    class AuthInfo:
        pass

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def wrap(self, cls: Type[T], data: Dict[str, Any]) -> T:

        if not isinstance(data, dict):
            raise ValueError("Invalid type of 'data', should be dict")

        valid_fields = {field.name for field in fields(cls)}

        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        return cls(**filtered_data)

    @abstractmethod
    def authenticate(self, *args, **kwargs) -> "Authentication.AuthInfo":
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError
