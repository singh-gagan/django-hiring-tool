from enum import Enum


class ActivityStatus(Enum):
    NOT_YET_STARTED = 'not_yet_started'
    STARTED = 'started'
    SUBMITTED = 'submitted'
    EXPIRED = 'expired'
