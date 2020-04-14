import base64
import logging
from email.mime.text import MIMEText

import pytz
import requests
from apiclient import errors
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib import xsrfutil
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from hiringapp.constants import ActivityStatus
from mysite.settings import local_settings

from . import models
from .constants import (
    GOOGLE_AUTHENTICATION_HOST, GOOGLE_SIGN_IN_REDIRECTURI, SCOPES, EmailType)
from .models import CredentialsModel, MailModel

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


def get_flow():
    flow = flow_from_clientsecrets(
        local_settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=SCOPES,
        redirect_uri=GOOGLE_SIGN_IN_REDIRECTURI,
        prompt='consent'
    ) 
          
    return flow


def is_authenticated(user):
    credential=CredentialsModel.get_credentials(user)
    try:
        access_token = credential.access_token
        READ_ONLY_SCOPE=SCOPES[0]
        requests.get(READ_ONLY_SCOPE,headers={'Host': GOOGLE_AUTHENTICATION_HOST,'Authorization': access_token})
        return True                                   
    except:
        return False


def get_gmail_authorize_url(user):
    flow=get_flow()
    flow.params['state'] = xsrfutil.generate_token(local_settings.SECRET_KEY,user)
    return flow.step1_get_authorize_url()


def get_gmail_callback_credential(state,authorization_code,user):
    if not xsrfutil.validate_token(local_settings.SECRET_KEY, state,user):
        return None
    
    flow=get_flow()
    credential = flow.step2_exchange(authorization_code)
    return credential


def get_mail_service(user):
    credential=CredentialsModel.get_credentials(user)
    if credential is None or credential.invalid:
        flow=get_flow()
        flow.params['state'] = xsrfutil.generate_token(local_settings.SECRET_KEY,user)
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    service = build('gmail', 'v1', credentials=credential,cache_discovery=False)
    return service


def send_message(submission_invitation_host, user_id, message):
    service=get_mail_service(submission_invitation_host)
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
        return True
    except errors.HttpError as error:
        logging.error(error)
        return False    


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
    if email_type==EmailType.ACTIVITY_EXPIRED.value or email_type==EmailType.ACTIVITY_SOLUTION.value:
        message['to']=get_invitation_host_email(submission.invitation_host)
    else:    
        message['to']=submission.candidate_email
    message['subject']=mail.mail_subject
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def create_mail_body(submission,email_type,message):
    current_time_zone=pytz.timezone(local_settings.TIME_ZONE)

    activity_start_time=None
    time_left=None
    
    if submission.activity_start_time is not None:
        activity_start_time=submission.activity_start_time.astimezone(current_time_zone).strftime("%Y-%m-%d %H:%M:%S")
        time_left=(submission.end_time-timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
    
    mail_body_keywords={
        "candidate_name":submission.candidate_name,
        "activity_duration":submission.activity_duration,
        "activity_url":local_settings.HOST+reverse('submission_invite',args=(submission.activity_uuid,)),
        "activity_start_time":activity_start_time,
        "activity_solution":submission.activity_solution_link,
        "candidate_email":submission.candidate_email,
        "time_left":time_left,
    }

    mail_body=message.format( **mail_body_keywords )
    
    return mail_body
