from django.db import models
from django.contrib import admin
from .utils import ActivityStatus,EmailType
import uuid
from django.contrib.auth.models import User 
from oauth2client.contrib.django_util.models import CredentialsField 
#Create your models here.

class Submission(models.Model):

    candidate_name=models.CharField(max_length=200)
    candidate_email=models.EmailField(max_length = 254)
    activity_duration=models.TimeField(auto_now=False,auto_now_add=False)
    activity_start_time=models.DateTimeField(blank=True,null=True)
    activity_drive_link= models.URLField(max_length = 500)
    activity_uuid= models.UUIDField(primary_key = True, default = uuid.uuid4())
    activity_solution_link= models.URLField(max_length = 500,blank=True,null=True)
    reminder_for_submission_time=models.TimeField(auto_now=False,auto_now_add=False)
    activity_status=models.CharField(
        max_length = 500,
        choices=[(tag, tag.value) for tag in ActivityStatus],
        default=ActivityStatus.Not_Yet_Started
    )

    def __str__(self):
        str="Invitation No.{}".format(self.pk)
        return str


class CredentialsModel(models.Model): 
    id = models.ForeignKey(User, primary_key = True, on_delete = models.CASCADE) 
    credential = CredentialsField() 

class CredentialsAdmin(admin.ModelAdmin): 
    pass


class MailModel(models.Model):
    mail_type=models.CharField(
        max_length=100,
        choices=[(key.value, key.name) for key in EmailType],
        unique=True,
        default=EmailType.Invitation,
    )
    mail_subject=models.CharField(max_length=100)
    mail_content=models.CharField(max_length=1000)

    def __str__(self):
        return self.mail_type