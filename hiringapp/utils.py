from enum import Enum
import uuid
from oauth2client.client import flow_from_clientsecrets
from mysite import settings
from . import models
from email.mime.text import MIMEText
import base64
from django.utils.dateparse import parse_duration

class ActivityStatus(Enum):
        NOTYETSTARTED='not_yet_started'
        STARTED='started'
        SUBMITTED='submitted'
        EXPIRED='expired'


class EmailType(Enum):
        INVITATION='invitation'
        REMINDER='reminder'
        ACTIVITYEXPIRED='activity_expired'
        ACTIVITYSOLUTION='activity_solution'
        SUBMISSIONREMINDER='reminder_to_submit'


FLOW = flow_from_clientsecrets(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=['https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose'],
        redirect_uri='http://127.0.0.1:8000/oauth2callback',
        prompt='consent')