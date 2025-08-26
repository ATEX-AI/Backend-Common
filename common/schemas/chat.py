# -*- coding: utf-8 -*-
from typing import Union

from pydantic import BaseModel

from common.schemas.info_flow import InfoFlowType, ConfigDict


class ChatMetaData(BaseModel):
    username: str | None = None
    chat_id: str | None = None
    chat_type: str | None = None
    name: str | None = None
    avatar: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="allow")

class ChatBase(BaseModel):
    id: int
    info_flow_id: int
    messenger_chat_id: str
    company_id: int
    is_blocked: bool
    type: InfoFlowType
    meta: Union[ChatMetaData, None] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")