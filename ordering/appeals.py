from enum import Enum


class AppealsStatsOrderFilters(str, Enum):
    ID = "id"
    STATUS = "status"
    INFO_FLOW_ID = "info_flow_id"
    CLIENT = "client"
    WORKER = "worker"
    CLOSING_DATE = "closing_date"
    CSI = "csi"