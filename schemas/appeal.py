from enum import Enum
from datetime import datetime

from pydantic import BaseModel

from schemas.user import UserBase


class AppealPeriodFilterOption(str, Enum):
    last_message = "last_message"
    appeal_creation_date = "appeal_creation_date"


class FixedQueuesTypes(str, Enum):
    common_queue = "common_queue"
    unallocated_queue = "unallocated_queue"
    archive_queue = "archive_queue"


class AppealStatus(str, Enum):
    new = "new"
    # open = "open"
    in_work = "in_work"
    on_pause = "on_pause"
    closed = "closed"
    # client_awaiting = "client_awaiting"
    # closed_not_rated = "closed_not_rated"
    # closed_shall_rate = "closed_shall_rate"
    # closed_by_admin = "closed_by_admin"
    # closed_by_timeout = "closed_by_timeout"


class AppealBase(BaseModel):
    id: int
    chat_id: int
    company_id: int
    status: AppealStatus
    needs_an_operator: bool
    unread_messages_cnt: int
    operator: int | None


class AppealDetails(BaseModel):

    id: int
    chat_id: int
    number: int
    company_id: int
    status: AppealStatus
    unread_messages_cnt: int
    operator: UserBase
    client: UserBase
    is_ruled_by_bot: bool | None
    creation_date: datetime | None
    last_message_date: datetime | None
    closing_date: datetime | None
    chat_type: str | None

