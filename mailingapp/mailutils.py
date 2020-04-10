import httplib2
from googleapiclient.discovery import build
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from . import models
from django.urls import reverse
from oauth2client.contrib import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from django.shortcuts import render,redirect
from httplib2 import Http
from apiclient import errors
from email.mime.text import MIMEText
import base64
from oauth2client import service_account
from django.contrib import messages
from django.views.generic.edit import FormView
from mysite import settings
from .constants import EmailType


def get_flow():
    FLOW = flow_from_clientsecrets(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scope=['https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose'],
        redirect_uri='http://127.0.0.1:8000/oauth2callback',
        prompt='consent')
    return FLOW



def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)    


def get_mail_service(user):
    storage = DjangoORMStorage(models.CredentialsModel, 'id', user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid:
        FLOW=get_flow()
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,user)
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
    mail=models.MailModel.objects.get(mail_type=email_type)
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
    mail_body=""
    activity_invite_url="127.0.0.1:8000"+reverse('submission_invite',args=(submission.activity_uuid,))
    if email_type==EmailType.STARTREMINDER.value:
        mail_body=message.format(candidate_name=submission.candidate_name,activity_duration=submission.activity_duration,activity_url=activity_invite_url)
    elif email_type==EmailType.INVITATION.value:
        mail_body=message.format(candidate_name=submission.candidate_name,activity_duration=submission.activity_duration,activity_url=activity_invite_url)
    elif email_type==EmailType.SUBMISSIONREMINDER.value:
        mail_body=message.format(candidate_name=submission.candidate_name,time_left=submission.reminder_for_submission_time,activity_url=activity_invite_url)
    elif email_type==EmailType.ACTIVITYEXPIRED.value:
        mail_body=message.format(candidate_name=submission.candidate_name,candidate_email=submission.candidate_email,activity_start_time=submission.activity_start_time)
    elif email_type==EmailType.ACTIVITYSOLUTION.value:
        mail_body=message.format(candidate_name=submission.candidate_name,candidate_email=submission.candidate_email,activity_solution=submission.activity_solution_link)    
    return mail_body
        
