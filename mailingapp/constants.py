from enum import Enum

class EmailType(Enum):
        INVITATION='invitation'
        REMINDER='reminder'
        ACTIVITYEXPIRED='activity_expired'
        ACTIVITYSOLUTION='activity_solution'
        SUBMISSIONREMINDER='reminder_to_submit'