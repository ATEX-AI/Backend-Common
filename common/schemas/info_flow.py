from enum import Enum

from pydantic import BaseModel


class InfoFlowType(str, Enum):
    telegram = "telegram"
    instagram = "instagram"


class InfloFlowStatus(str, Enum):
    valid = "valid"
    invalid = "invalid"


class InfoFlowBase(BaseModel):
    id: int
    company_id: int
    # operators_group: List[int] | None # not for mvp
    avatar: str | None = None
    name: str | None
    type: InfoFlowType
