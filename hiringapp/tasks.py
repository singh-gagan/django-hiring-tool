import string
from .utils import create_invite_message
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task

"""
@shared_task
def sent_invite_mail(submission):
    message=create_invite_message(submission)
""" 