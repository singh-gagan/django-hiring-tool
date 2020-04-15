import logging

import requests
from apiclient import errors
from django.contrib import messages
from django.http import HttpResponseRedirect
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib import xsrfutil

from mysite.settings import local_settings

from .constants import (
    GOOGLE_AUTHENTICATION_HOST, GOOGLE_SIGN_IN_REDIRECTURI, SCOPES)
from .models import GmailCredential

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
