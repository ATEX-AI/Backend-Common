from enum import Enum
from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class ServiceBotsStatsHeader:
    title: str
    key: str


class ServiceBotsStatsHeaderSchema(BaseModel):
    title: str = Field(...)
    key: str = Field(...)

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class ServiceBotsStatsTableColumns(str, Enum):
    all = "*"
    service_bot = "service_bot"
    appeals_cnt = "appeals_cnt"
    messages_cnt = "messages_cnt"
    leads_cnt = "leads_cnt"
    leads_and_common_appeals = "leads_and_common_appeals"
    automatization_percentage = "automatization_percentage"


class ServiceBotsStatsTableHeaders(Enum):
    rus = [
        ServiceBotsStatsHeader(
            "Чат-бот", ServiceBotsStatsTableColumns.service_bot.value
        ),
        ServiceBotsStatsHeader(
            "Обращения", ServiceBotsStatsTableColumns.appeals_cnt.value
        ),
        ServiceBotsStatsHeader(
            "Сообщения", ServiceBotsStatsTableColumns.messages_cnt.value
        ),
        ServiceBotsStatsHeader("Лиды", ServiceBotsStatsTableColumns.leads_cnt.value),
        ServiceBotsStatsHeader(
            "Лиды/ Общ.заявки",
            ServiceBotsStatsTableColumns.leads_and_common_appeals.value,
        ),
        ServiceBotsStatsHeader(
            "% Автоматизации",
            ServiceBotsStatsTableColumns.automatization_percentage.value,
        ),
    ]
    eng = [
        ServiceBotsStatsHeader(
            "Chat-bot", ServiceBotsStatsTableColumns.service_bot.value
        ),
        ServiceBotsStatsHeader(
            "Appeals", ServiceBotsStatsTableColumns.appeals_cnt.value
        ),
        ServiceBotsStatsHeader(
            "Messages", ServiceBotsStatsTableColumns.messages_cnt.value
        ),
        ServiceBotsStatsHeader("Leads", ServiceBotsStatsTableColumns.leads_cnt.value),
        ServiceBotsStatsHeader(
            "Leads / Total Appeals",
            ServiceBotsStatsTableColumns.leads_and_common_appeals.value,
        ),
        ServiceBotsStatsHeader(
            "% Automation", ServiceBotsStatsTableColumns.automatization_percentage.value
        ),
    ]
    uzb = [
        ServiceBotsStatsHeader(
            "Chat-bot", ServiceBotsStatsTableColumns.service_bot.value
        ),
        ServiceBotsStatsHeader(
            "Murojaatlar", ServiceBotsStatsTableColumns.appeals_cnt.value
        ),
        ServiceBotsStatsHeader(
            "Xabarlar", ServiceBotsStatsTableColumns.messages_cnt.value
        ),
        ServiceBotsStatsHeader("Lidlar", ServiceBotsStatsTableColumns.leads_cnt.value),
        ServiceBotsStatsHeader(
            "Lidlar / Umumiy murojaatlar",
            ServiceBotsStatsTableColumns.leads_and_common_appeals.value,
        ),
        ServiceBotsStatsHeader(
            "Avtomatlashtirish %",
            ServiceBotsStatsTableColumns.automatization_percentage.value,
        ),
    ]

    def as_pydantic(self) -> List[ServiceBotsStatsHeaderSchema]:
        return [
            ServiceBotsStatsHeaderSchema.model_validate(h.__dict__) for h in self.value
        ]
