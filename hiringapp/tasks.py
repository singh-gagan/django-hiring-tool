import string
from .utils import create_invite_message
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .mailutils import get_mail_service,send_message
from celery import shared_task
from . import models
@shared_task
def send_invite_mail(id):
    submission=models.Submission.objects.get(activity_uuid=id)
    try:
        message=create_invite_message(submission)
        service=get_mail_service(submission.invitation_host)
        sent = send_message(service,'me', message)
        print('Mail sent successfully')
    except:
        print('Mail not sent')
    return "celery_task_executed"