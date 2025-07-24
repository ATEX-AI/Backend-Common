from typing import Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict


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


class InfoFlowTechData(BaseModel):
    token: Optional[str] = None
    greeting: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")


class InfoFlowVisibleTechData(BaseModel):
    greeting: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
