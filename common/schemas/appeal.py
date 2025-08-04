from enum import Enum
from typing import Union
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from common.schemas.user import UserBase


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
    operator: Union[int, None] = None
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class AppealDetails(BaseModel):

    id: int
    chat_id: int
    number: int
    company_id: int
    status: AppealStatus
    unread_messages_cnt: int
    operator: UserBase
    client: UserBase
    is_ruled_by_bot: Union[bool, None] = None
    creation_date: Union[datetime, None] = None
    last_message_date: Union[datetime, None] = None
    closing_date: Union[datetime, None] = None
    chat_type: Union[str, None] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")