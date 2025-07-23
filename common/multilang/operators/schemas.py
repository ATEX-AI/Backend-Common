from enum import Enum
from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class OperatorsStatsHeader:
    title: str
    key: str


class OperatorsStatsHeaderSchema(BaseModel):
    title: str = Field(...)
    key: str = Field(...)

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class OperatorsStatsTableColumns(str, Enum):
    all = "*"
    operator = "operator"
    info_flow = "info_flow"
    appeals_cnt = "appeals_cnt"
    appeals_accepted_cnt = "appeals_accepted_cnt"
    appeals_closed_cnt = "appeals_closed_cnt"
    appeals_missed_cnt = "appeals_missed_cnt"
    mean_response_time_in_seconds = "mean_response_time_in_seconds"
    mean_pending_time_in_seconds = "mean_pending_time_in_seconds"


class AppealsStatsTableHeaders(Enum):
    rus = [
        OperatorsStatsHeader("Статус", OperatorsStatsTableColumns.operator.value),
        OperatorsStatsHeader("Канал", OperatorsStatsTableColumns.info_flow.value),
        OperatorsStatsHeader("Обращения", OperatorsStatsTableColumns.appeals_cnt.value),
        OperatorsStatsHeader(
            "Принято", OperatorsStatsTableColumns.appeals_accepted_cnt.value
        ),
        OperatorsStatsHeader(
            "Закрыто", OperatorsStatsTableColumns.appeals_closed_cnt.value
        ),
        OperatorsStatsHeader(
            "Пропущено", OperatorsStatsTableColumns.appeals_missed_cnt.value
        ),
        OperatorsStatsHeader(
            "Сред. время ответа (с)",
            OperatorsStatsTableColumns.mean_response_time_in_seconds.value,
        ),
        OperatorsStatsHeader(
            "Сред. время ожидания (с)",
            OperatorsStatsTableColumns.mean_pending_time_in_seconds.value,
        ),
    ]
    eng = [
        OperatorsStatsHeader("Status", OperatorsStatsTableColumns.operator.value),
        OperatorsStatsHeader("Channel", OperatorsStatsTableColumns.info_flow.value),
        OperatorsStatsHeader("Appeals", OperatorsStatsTableColumns.appeals_cnt.value),
        OperatorsStatsHeader(
            "Accepted", OperatorsStatsTableColumns.appeals_accepted_cnt.value
        ),
        OperatorsStatsHeader(
            "Closed", OperatorsStatsTableColumns.appeals_closed_cnt.value
        ),
        OperatorsStatsHeader(
            "Missed", OperatorsStatsTableColumns.appeals_missed_cnt.value
        ),
        OperatorsStatsHeader(
            "Avg. Response Time (s)",
            OperatorsStatsTableColumns.mean_response_time_in_seconds.value,
        ),
        OperatorsStatsHeader(
            "Avg. Pending Time (s)",
            OperatorsStatsTableColumns.mean_pending_time_in_seconds.value,
        ),
    ]
    uzb = [
        OperatorsStatsHeader("Holat", OperatorsStatsTableColumns.operator.value),
        OperatorsStatsHeader(
            "Axborot oqimi", OperatorsStatsTableColumns.info_flow.value
        ),
        OperatorsStatsHeader(
            "Murojaatlar", OperatorsStatsTableColumns.appeals_cnt.value
        ),
        OperatorsStatsHeader(
            "Qabul qilingan", OperatorsStatsTableColumns.appeals_accepted_cnt.value
        ),
        OperatorsStatsHeader(
            "Yopilgan", OperatorsStatsTableColumns.appeals_closed_cnt.value
        ),
        OperatorsStatsHeader(
            "O'tkazib yuborilgan", OperatorsStatsTableColumns.appeals_missed_cnt.value
        ),
        OperatorsStatsHeader(
            "O'rt. javob vaqti (s)",
            OperatorsStatsTableColumns.mean_response_time_in_seconds.value,
        ),
        OperatorsStatsHeader(
            "O'rt. kutilish vaqti (s)",
            OperatorsStatsTableColumns.mean_pending_time_in_seconds.value,
        ),
    ]

    def as_pydantic(self) -> List[OperatorsStatsHeaderSchema]:
        return [
            OperatorsStatsHeaderSchema.model_validate(h.__dict__) for h in self.value
        ]
