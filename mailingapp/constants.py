from enum import Enum


class EmailType(Enum):
        INVITATION='invitation'
        STARTREMINDER='reminder'
        ACTIVITYEXPIRED='activity_expired'
        ACTIVITYSOLUTION='activity_solution'
        SUBMISSIONREMINDER='reminder_to_submit'

SCOPES=['https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose']

GOOGLE_SIGN_IN_REDIRECTURI='http://127.0.0.1:8000/oauth2callback'


GOOGLE_AUTHENTICATION_HOST='www.googleapis.com'
