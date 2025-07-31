# -*- coding: utf-8 -*-
from typing import List, Union
from decimal import Decimal
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ServiceBotStatsTypes(str, Enum):
    all = "all"
    appeals_cnt = "appeals_cnt"
    messages_cnt = "messages_cnt"
    leads_cnt = "leads_cnt"
    leads_and_common_appeals = "leads_and_common_appeals"
    automatization_percentage = "automatization_percentage"


class ServiceBotBase(BaseModel):
    id: int
    uuid_id: UUID
    prompt: str
    talkativeness: Decimal
    temperature: Decimal
    timezone: str
    settings: Union[List, dict, None]
    name: Union[str, None]
    avatar: Union[str, None]

    model_config = ConfigDict(from_attributes=True)
