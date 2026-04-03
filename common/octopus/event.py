from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json


@dataclass
class OctopusEvent:
    type: str                    # "chat.completed", "lead.created", "content.posted"
    company_id: int
    bot_id: int | None = None
    timestamp: str = ""
    data: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, default=str)

    @classmethod
    def from_json(cls, raw: str) -> "OctopusEvent":
        d = json.loads(raw)
        return cls(**d)
