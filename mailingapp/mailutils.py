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

from .constants import (
    GOOGLE_AUTHENTICATION_HOST, GOOGLE_SIGN_IN_REDIRECTURI, SCOPES, EmailType)
from .models import EmailTemplate, GmailCredential


log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("mails.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class GmailServices:

    @classmethod
    def get_flow(cls,):
        flow = flow_from_clientsecrets(
        local_settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=SCOPES,
        redirect_uri=GOOGLE_SIGN_IN_REDIRECTURI,
        prompt='consent'
        ) 
        
        return flow

    @classmethod
    def is_gmail_authenticated(cls,user):
        credential=GmailCredential.get_credentials(user)
        try:
            access_token = credential.access_token
            READ_ONLY_SCOPE=SCOPES[0]
            requests.get(READ_ONLY_SCOPE,headers={'Host': GOOGLE_AUTHENTICATION_HOST,'Authorization': access_token})
            return True                                   
        except:
            return False

    @classmethod
    def get_gmail_authorize_url(cls,user):
        flow=cls.get_flow()
        flow.params['state'] = xsrfutil.generate_token(local_settings.SECRET_KEY,user)
        return flow.step1_get_authorize_url()

    @classmethod
    def get_gmail_auth_callback_credential(cls,state,authorization_code,user):
        if not xsrfutil.validate_token(local_settings.SECRET_KEY, state,user):
            return None
    
        flow=cls.get_flow()
        credential = flow.step2_exchange(authorization_code)
        return credential

    @classmethod
    def get_gmail_service(cls,user):
        credential=GmailCredential.get_credentials(user)
        if credential is None or credential.invalid:
            flow=cls.get_flow()
            flow.params['state'] = xsrfutil.generate_token(local_settings.SECRET_KEY,user)
            authorize_url = flow.step1_get_authorize_url()
            return HttpResponseRedirect(authorize_url)
        service = build('gmail', 'v1', credentials=credential,cache_discovery=False)
        return service

    @classmethod
    def send_message(cls,submission_invitation_host,message):
        service=cls.get_gmail_service(submission_invitation_host)
        try:
            message = (service.users().messages().send(userId='me', body=message)
                   .execute())
            return message
        except errors.HttpError as error:
            logger.error("error while sending mails"+error)
            return None

    @classmethod
    def get_invitation_host_email(cls,invitation_host):
        service=cls.get_gmail_service(invitation_host)
        profile = service.users().getProfile(userId='me').execute()
        return profile['emailAddress']


class GmailUtils:


    @classmethod
    def create_messages(cls,submission,email_type):
        #logic to create message from submission details and email_type 
        mail=EmailTemplate.get_mail(email_type)
        message=mail.mail_content
        mail_body=""
        mail_body=cls.create_mail_body(submission,email_type,message)
        message=MIMEText(mail_body,'html')
        if email_type==EmailType.ACTIVITY_EXPIRED.value or email_type==EmailType.ACTIVITY_SOLUTION.value:
            message['to']=GmailServices.get_invitation_host_email(submission.invitation_host)
        else:    
            message['to']=submission.candidate_email
        message['subject']=mail.mail_subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    @classmethod
    def create_mail_body(cls,submission,email_type,message):
        current_time_zone=pytz.timezone(local_settings.TIME_ZONE)
            
        mail_body_keywords={
            "candidate_name":submission.candidate_name,
            "activity_duration":submission.activity_duration,
            "activity_url":local_settings.HOST+reverse('submission_invite',args=(submission.activity_uuid,)),
            "activity_start_time":"" if submission.activity_start_time is None else submission.activity_start_time.astimezone(current_time_zone).strftime("%Y-%m-%d %H:%M:%S"),
            "activity_solution_link":submission.activity_solution_link,
            "candidate_email":submission.candidate_email,
            "time_left":"" if submission.time_left is None else (str(submission.time_left.days)+" days "+str(submission.time_left.seconds//3600)+" hours "+str((submission.time_left.seconds//60)%60)+" minutes ")
        }

        mail_body=message.format( **mail_body_keywords )
        
        return mail_body
