from typing import List
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from multilang.schemas import Language


@dataclass(frozen=True)
class StatusLabel:
    rus: str
    eng: str
    uzb: str


@dataclass(frozen=True)
class AppealStatsHeader:
    title: str
    key: str


class AppealStatsHeaderSchema(BaseModel):
    title: str
    key: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class AppealMultiLangStatus(Enum):
    new = StatusLabel(rus="Новая", eng="New", uzb="Yangi")
    open = StatusLabel(rus="Открытая", eng="Open", uzb="Ochilgan")
    in_work = StatusLabel(rus="В работе", eng="In Progress", uzb="Jarayonda")
    on_pause = StatusLabel(rus="Приостановлена", eng="Paused", uzb="To'xtatilgan")
    closed = StatusLabel(rus="Закрыта", eng="Closed", uzb="Yopilgan")

    def __getitem__(self, language: Language) -> str:
        return getattr(self.value, language.name, self.value.eng)


class AppealStatsTableColumns(str, Enum):
    all = "*"
    status = "status"
    info_flow = "info_flow"
    client = "client"
    worker = "worker"
    closing_date = "closing_date"
    csi = "csi"


class AppealsStatsTableHeaders(Enum):
    rus = [
        AppealStatsHeader(title="Статус", key=AppealStatsTableColumns.status.value),
        AppealStatsHeader(
            title="Инфо-поток", key=AppealStatsTableColumns.info_flow.value
        ),
        AppealStatsHeader(title="Клиент", key=AppealStatsTableColumns.client.value),
        AppealStatsHeader(
            title="Исполнитель", key=AppealStatsTableColumns.worker.value
        ),
        AppealStatsHeader(
            title="Дата закрытия", key=AppealStatsTableColumns.closing_date.value
        ),
        AppealStatsHeader(title="CSI", key=AppealStatsTableColumns.csi.value),
    ]
    eng = [
        AppealStatsHeader(title="Status", key=AppealStatsTableColumns.status.value),
        AppealStatsHeader(
            title="Info Flow", key=AppealStatsTableColumns.info_flow.value
        ),
        AppealStatsHeader(title="Client", key=AppealStatsTableColumns.client.value),
        AppealStatsHeader(title="Worker", key=AppealStatsTableColumns.worker.value),
        AppealStatsHeader(
            title="Closing Date", key=AppealStatsTableColumns.closing_date.value
        ),
        AppealStatsHeader(title="CSI", key=AppealStatsTableColumns.csi.value),
    ]
    uzb = [
        AppealStatsHeader(title="Holat", key=AppealStatsTableColumns.status.value),
        AppealStatsHeader(
            title="Axborot oqimi", key=AppealStatsTableColumns.info_flow.value
        ),
        AppealStatsHeader(title="Mijoz", key=AppealStatsTableColumns.client.value),
        AppealStatsHeader(title="Xodim", key=AppealStatsTableColumns.worker.value),
        AppealStatsHeader(
            title="Yopilish sanasi", key=AppealStatsTableColumns.closing_date.value
        ),
        AppealStatsHeader(title="CSI", key=AppealStatsTableColumns.csi.value),
    ]

    def as_pydantic(self) -> List[AppealStatsHeaderSchema]:
        return [AppealStatsHeaderSchema.model_validate(h.__dict__) for h in self.value]
