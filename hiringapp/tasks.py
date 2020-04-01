import string
from .mailutils import create_messages
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .mailutils import get_mail_service,send_message
from celery import shared_task
from . import models
from .utils import EmailType
from django.utils import timezone

@shared_task
def send_emails_to_candidates(id,email_type):
    submission=models.Submission.objects.get(activity_uuid=id)
    try:
        message=create_messages(submission,email_type)
        service=get_mail_service(submission.invitation_host)
        sent = send_message(service,'me', message)
        models.MailSummary.objects.create(mail_type=email_type,activity_uuid=id,candidate_name=submission.candidate_name,date_of_mail=timezone.now())     
        print('Mail sent successfully')
    except:
        print('Mail not sent')
    return "celery_task_executed"


