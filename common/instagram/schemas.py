from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class AppealStatus(str, Enum):
    new = "new"
    open = "open"
    in_work = "in_work"
    on_pause = "on_pause"
    # client_awaiting = "client_awaiting"
    # closed_not_rated = "closed_not_rated"
    # closed_shall_rate = "closed_shall_rate"
    # closed_by_admin = "closed_by_admin"
    # closed_by_timeout = "closed_by_timeout"


@dataclass
class Appeal:
    id: int = None
    status: str = None
    needs_an_operator: bool = None


@dataclass
class AppealMessage:
    id: int = None
    status: str = None
    needs_an_operator: bool = None
    operator: int | None = None
    chat_id: int | None = None
    number: int = None
    last_message: str = None
    last_message_date: datetime = None
    unread_messages_cnt: int = None
    company_id: int | None = None


class MessageType(str, Enum):
    text = "text"
    audio = "audio"
    image = "image"


@dataclass
class Message:
    id: int = None
    chat_id: str = None
    date: str | datetime = None
    is_sent_by_bot: bool = None
    is_sent_by_service: bool = None
    message: str = None
    type: str = MessageType.text
    image: str = None

    appeal: AppealMessage = None
