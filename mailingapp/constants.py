from enum import Enum

from mysite.settings import local_settings


class EmailType(Enum):
        INVITATION='invitation'
        START_REMINDER='reminder_to_start'
        ACTIVITY_EXPIRED='activity_expired'
        ACTIVITY_SOLUTION='activity_solution'
        SUBMISSION_REMINDER='reminder_to_submit'

SCOPES=['https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose']

GOOGLE_SIGN_IN_REDIRECTURI='http://'+local_settings.HOST+'/gmail/oauth2callback'


GOOGLE_AUTHENTICATION_HOST='www.googleapis.com'
