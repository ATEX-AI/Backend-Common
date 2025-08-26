# -*- coding: utf-8 -*-
from typing import Union

from pydantic import BaseModel

from common.schemas.info_flow import InfoFlowType, ConfigDict


class ChatMetaData(BaseModel):
    username: int | str | None = None
    chat_id: int | str | None = None
    chat_type: int | str | None = None
    name: int | str | None = None
    avatar: int | str | None = None

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