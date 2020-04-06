from enum import Enum
import uuid
from oauth2client.client import flow_from_clientsecrets
from mysite import settings
from . import models
from email.mime.text import MIMEText
import base64
from django.utils.dateparse import parse_duration

class ActivityStatus(Enum):
        Not_Yet_Started='not_yet_started'
        Started='started'
        Submitted='submitted'
        Expired='expired'


class EmailType(Enum):
        Invitation='invitation'
        Reminder='reminder'
        ActivityExpired='activity_expired'
        ActivitySolution='activity_solution'
        SubmissionReminder='reminder_to_submit'


FLOW = flow_from_clientsecrets(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=['https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose'],
        redirect_uri='http://127.0.0.1:8000/admin/oauth2callback',
        prompt='consent')