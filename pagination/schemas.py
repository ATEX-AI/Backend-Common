from typing import List, TypeVar, Generic

from pydantic import BaseModel


T = TypeVar("T")


class LimitOffsetPaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    results: List[T]


class PagePaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    pages: int
    results: List[T]
