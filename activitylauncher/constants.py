from enum import Enum


class ActivityStatus(Enum):
    NOT_YET_STARTED = "not_yet_started"
    STARTED = "started"
    SUBMITTED = "submitted"
    EXPIRED = "expired"


ActivityInstructions = (
    "1. The time left to submit the solution is displayed above the activity.\n"
    + "2. You can close the activity in between however the timer will not stop\n"
    + "3. You are allowed to submit the solution only once.\n"
    + "4. Submit only the link to the solution which can be a github link or drive link\n"
)
