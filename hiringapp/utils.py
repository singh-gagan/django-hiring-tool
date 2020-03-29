from enum import Enum
import uuid
from oauth2client.client import flow_from_clientsecrets
from mysite import settings
class ActivityStatus(Enum):
        Started='started'
        Submitted='submitted'
        Not_Yet_Started='not_yet_started'
        Expired='expired'



FLOW = flow_from_clientsecrets(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=['https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose'],
        redirect_uri='http://127.0.0.1:8000/oauth2callback',
        prompt='consent')