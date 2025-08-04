# -*- coding: utf-8 -*-
from typing import List, Union, Optional
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
    id: Optional[int] = None
    uuid_id: Optional[UUID] = None
    company_id: Optional[int] = None
    prompt: Optional[str] = None
    talkativeness: Optional[Decimal] = None
    temperature: Optional[Decimal] = None
    timezone: Optional[str] = None
    settings: Union[List, dict, None] = None
    name: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
