from enum import Enum
import uuid
from oauth2client.client import flow_from_clientsecrets
from mysite import settings
from . import models
from email.mime.text import MIMEText
import base64
from django.utils.dateparse import parse_duration
class ActivityStatus(Enum):
        Started='started'
        Submitted='submitted'
        Not_Yet_Started='not_yet_started'
        Expired='expired'


class EmailType(Enum):
        Invitation='invitation'
        Reminder='reminder'
        Feedback='feedback'


FLOW = flow_from_clientsecrets(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=['https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose'],
        redirect_uri='http://127.0.0.1:8000/admin/oauth2callback',
        prompt='consent')


def create_invite_message(submission):
        #logic to create message from submission details and 'invite mail' details 
        invitation=models.MailModel.objects.get(mail_type='invitation')
        message=invitation.mail_content
        mail_body=message.format(candidate_name=submission.candidate_name,activity_duration=submission.activity_duration,activity_uuid=submission.activity_uuid)
        message=MIMEText(mail_body,'html')
        message['to']=submission.candidate_email
        message['subject']=invitation.mail_subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

        
