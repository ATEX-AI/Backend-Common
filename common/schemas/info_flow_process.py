from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class InfoFlowProcessStatus(str, Enum):
    active = "active"
    starting = "starting"
    unknown = "unknown"
    dead = "dead"


class InfoFlowProcessBase(BaseModel):
    info_flow_id: int
    needs_an_update: bool
    need_a_restart: bool
    must_be_destroyed: bool
    process_pid: int
    process_start_time: datetime
    process_ping_time: datetime
    process_status: InfoFlowProcessStatus
    running_mode: str
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")
