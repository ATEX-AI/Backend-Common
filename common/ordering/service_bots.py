from enum import Enum


class ServiceBotsStatsOrderFilters(str, Enum):
    NAME = "name"
    APPEALS_CNT = "appeals_cnt"
    MESSAGES_CNT = "messages_cnt"
    LEADS_CNT = "leads_cnt"
    LEADS_AND_COMMON_APPEALS = "leads_and_common_appeals"
    AUTOMATIZATION_PERCENTAGE = "automatization_percentage"