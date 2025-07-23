import uuid
import time
from typing import Any, Dict
from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    send_message = "send_message"
    handle_message = "handle_message"
    # drop_message = "drop_message"
    # edit_message = "edit_message"
    update_tech_info = "update_tech_info"
    check_bot = "check_bot"
    drop_bot = "drop_bot"


class Task(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Description for spec. task, may contains comments, instructions, etc.",
    )
    type: TaskType = Field(
        ...,
        description="Type of the task (e.g. send_message, drop_message, edit_message, drop_bot, check_bot, handle_message).",
    )
    payload: Dict[str, Any] = Field(..., description="Data for the specified task.")
    timestamp: float = Field(
        default_factory=lambda: time.time(),
        description="The time the task was created (unix timestamp).",
    )
