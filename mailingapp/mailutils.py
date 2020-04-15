import base64
import logging
from email.mime.text import MIMEText

import pytz
from django.urls import reverse
from django.utils import timezone

from mysite.settings import local_settings

from .constants import EmailType
from .mailservices import GmailServices
from .models import EmailTemplate

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("mails.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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
