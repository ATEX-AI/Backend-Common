# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

# ==== Message ==== #


class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    FILE = "file"


class MessageBase(BaseModel):
    id: int
    type: MessageType
    date: datetime
    message: str
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")
