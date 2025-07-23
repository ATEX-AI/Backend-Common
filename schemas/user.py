from typing import List, Optional
from enum import Enum

from pydantic import BaseModel


class UserType(str, Enum):
    bot = "bot"
    service = "service"
    user = "user"


class UserRole(str, Enum):
    admin = "admin"
    operator = "operator"


class UserBase(BaseModel):
    type: UserType
    id: Optional[int] = None
    name: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
