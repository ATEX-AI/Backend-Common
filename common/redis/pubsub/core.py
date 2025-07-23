from abc import ABC
from enum import Enum
from typing import Any, Protocol, Optional, Type, Dict

from pydantic import BaseModel


class BaseEventType(str, Enum):
    pass


class EventPayload(BaseModel):
    event: BaseEventType
    data: Dict[str, Any]


class ConnectionLike(Protocol):
    async def receive_text(self) -> str: ...
    async def send_text(self, data: str) -> None: ...
    async def close(self, *, code: int, reason: str | None = None) -> None: ...
    async def accept(self) -> None: ...


class _EventRegistry(ABC):
    def __init__(
        self,
        *,
        events_cls: Optional[Type[BaseEventType]] = None,
        events_payload_cls: Optional[Type[EventPayload]] = None
    ) -> None:
        self._events_cls = events_cls
        self._events_payload_cls = events_payload_cls

    def _is_registered(self, ev: BaseEventType) -> bool:
        return self._events_cls is None or isinstance(ev, self._events_cls)
