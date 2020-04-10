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

