from typing import Type, TypeVar, Dict, Any
from dataclasses import fields

T = TypeVar("T")


class DataClassWrapper:
    def __init__(self):
        pass

    def wrap(self, cls: Type[T], data: Dict[str, Any]) -> T:

        if not isinstance(data, dict):
            raise ValueError("Invalid type of 'data', should be dict")

        valid_fields = {field.name for field in fields(cls)}

        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        return cls(**filtered_data)
