from enum import Enum


class OperatorsStatsOrderFilters(str, Enum):
    NAME = "name"
    INFO_FLOW = "info_flow"
    APPEALS_CNT = "appeals_cnt"
    APPEALS_ACCEPTED_CNT = "appeals_accepted_cnt"
    APPEALS_CLOSED_CNT = "appeals_closed_cnt"
    APPEALS_MISSED_CNT = "appeals_missed_cnt"
    MEAN_RESPONSE_TIME = "mean_response_time"
    MEAN_PENDING_TIME = "mean_pending_time"