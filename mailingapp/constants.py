from enum import Enum


class EmailType(Enum):
    INVITATION = "invitation"
    START_REMINDER = "reminder_to_start"
    ACTIVITY_EXPIRED = "activity_expired"
    ACTIVITY_SOLUTION = "activity_solution"
    SUBMISSION_REMINDER = "reminder_to_submit"


class EmailTemplatePlaceholder(Enum):
    CANDIDATE_NAME = "candidate_name"
    CANDIDATE_EMAIL = "candidate_email"
    ACTIVITY_DURATION = "activity_duration"
    ACTIVITY_URL = "activity_url"
    ACTIVITY_START_TIME = "activity_start_time"
    ACTIVITY_SOLUTION_LINK = "activity_solution_link"
    ACTIVITY_LEFT_TIME = "activity_left_time"


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]


GOOGLE_AUTHENTICATION_HOST = "www.googleapis.com"
