# -*- coding: utf-8 -*-
from typing import Union

from pydantic import BaseModel

from common.schemas.info_flow import InfoFlowType, ConfigDict


class ChatBase(BaseModel):
    id: int
    info_flow_id: int
    messenger_chat_id: str
    company_id: int
    is_blocked: bool
    type: InfoFlowType
    meta: Union[dict, None] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")