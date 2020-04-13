from googleapiclient.discovery import build
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from . import models
from django.urls import reverse
from oauth2client.contrib import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from django.shortcuts import redirect
from apiclient import errors
from email.mime.text import MIMEText
import base64
from django.contrib import messages
from mysite.settings import local_settings
from .constants import EmailType
from .constants import SCOPES,GOOGLE_SIGN_IN_REDIRECTURI,GOOGLE_AUTHENTICATION_HOST
from .models import CredentialsModel,MailModel
import requests
import logging
import pytz

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

def get_flow():
    FLOW = flow_from_clientsecrets(
        local_settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=SCOPES,
        redirect_uri=GOOGLE_SIGN_IN_REDIRECTURI,
        prompt='consent')
    return FLOW

def get_authorize_url(user):
    FLOW=get_flow()
    FLOW.params['state'] = xsrfutil.generate_token(local_settings.SECRET_KEY,user)
    authorize_url = FLOW.step1_get_authorize_url()
    return authorize_url

def get_auth_return_credentials(state,authorization_code,user):
    if not xsrfutil.validate_token(local_settings.SECRET_KEY, state,user):
        return None
    FLOW=get_flow()
    credential = FLOW.step2_exchange(authorization_code)
    return credential


def authenticate(user):
    authorized = False
    credential=CredentialsModel.get_credentials(user)
    access_token=CredentialsModel.get_access_token(credential)
    if access_token is not None:
        READ_ONLY_SCOPE=SCOPES[0]
        requests.get(READ_ONLY_SCOPE,headers={'Host': GOOGLE_AUTHENTICATION_HOST,'Authorization': access_token})
        authorized=True                                    
    return authorized


def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
        return True
    except errors.HttpError as error:
        logging.error(error)
        return False    


def get_mail_service(user):
    credential=CredentialsModel.get_credentials(user)
    if credential is None or credential.invalid:
        FLOW=get_flow()
        FLOW.params['state'] = xsrfutil.generate_token(local_settings.SECRET_KEY,user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    service = build('gmail', 'v1', credentials=credential,cache_discovery=False)
    return service


def get_invitation_host_email(invitation_host):
    service=get_mail_service(invitation_host)
    profile = service.users().getProfile(userId='me').execute()
    return profile['emailAddress']


def create_messages(submission,email_type):
    #logic to create message from submission details and email_type 
    mail=MailModel.get_mail(email_type)
    message=mail.mail_content
    mail_body=""
    mail_body=create_mail_body(submission,email_type,message)
    message=MIMEText(mail_body,'html')
    if email_type==EmailType.ACTIVITYEXPIRED.value or email_type==EmailType.ACTIVITYSOLUTION.value:
        message['to']=get_invitation_host_email(submission.invitation_host)
    else:    
        message['to']=submission.candidate_email
    message['subject']=mail.mail_subject
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def create_mail_body(submission,email_type,message):
    time_zone=pytz.timezone(local_settings.TIME_ZONE)
    if submission.activity_start_time is not None:
        activity_start_time=submission.activity_start_time.astimezone(time_zone).strftime("%Y-%m-%d %H:%M:%S")

    mail_body=""
    activity_invite_url="127.0.0.1:8000"+reverse('submission_invite',args=(submission.activity_uuid,))
    
    if email_type==EmailType.STARTREMINDER.value:
        mail_body=message.format(candidate_name=submission.candidate_name,activity_duration=submission.activity_duration,activity_url=activity_invite_url)
    
    elif email_type==EmailType.INVITATION.value:
        mail_body=message.format(candidate_name=submission.candidate_name,activity_duration=submission.activity_duration,activity_url=activity_invite_url)
    
    elif email_type==EmailType.SUBMISSIONREMINDER.value:
        mail_body=message.format(candidate_name=submission.candidate_name,time_left=submission.reminder_for_submission_time,activity_url=activity_invite_url)
    
    elif email_type==EmailType.ACTIVITYEXPIRED.value:
        mail_body=message.format(candidate_name=submission.candidate_name,candidate_email=submission.candidate_email,activity_start_time=activity_start_time)
    
    elif email_type==EmailType.ACTIVITYSOLUTION.value:
        mail_body=message.format(candidate_name=submission.candidate_name,candidate_email=submission.candidate_email,activity_solution=submission.activity_solution_link)    
    
    return mail_body
