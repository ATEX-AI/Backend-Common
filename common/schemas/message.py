# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

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
