from django.db import models
from django.contrib.auth.models import User
from oauth2client.contrib.django_util.models import CredentialsField
from .constants import EmailType
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from django.utils import timezone
from datetime import datetime,timedelta

# Create your models here.

class CredentialsModel(models.Model): 
    id = models.OneToOneField(User, primary_key = True, on_delete = models.CASCADE) 
    credential = CredentialsField() 


    def __str__(self):
        return self.id.get_username()


    @classmethod
    def has_credentials(cls,user):
        return CredentialsModel.objects.filter(id=user).exists()
    
    
    
    @classmethod
    def get_credentials(cls,user):
        storage = DjangoORMStorage(CredentialsModel, 'id', user, 'credential')
        credential = storage.get()
        return credential    


    @classmethod
    def get_access_token(cls,credential):
      try:
        access_token=credential.access_token
        return access_token
      except:
        return None


    @classmethod
    def add_credentials(cls,user,credential):
        storage = DjangoORMStorage(CredentialsModel, 'id', user, 'credential')
        storage.put(credential)    


class MailModel(models.Model):
    mail_type=models.CharField(
        max_length=100,
        choices=[(key.value, key.name) for key in EmailType],
        unique=True,
        default=EmailType.INVITATION,
    )
    mail_subject=models.CharField(max_length=100)
    mail_content=models.CharField(max_length=1000)

    def __str__(self):
        return self.mail_type


class MailSummary(models.Model):

    MAIL_STATUS = (
        ('SENT', 'Sent'),
        ('NOTSENT', 'NotSent'),
    )

    mail_type=models.CharField(
        max_length=100,
        choices=[(key.value, key.name) for key in EmailType],
        default=EmailType.INVITATION,
    )
    activity_uuid=models.UUIDField(null=True)
    candidate_name=models.CharField(max_length=200)
    date_of_mail=models.DateTimeField(blank=True,null=True)
    mail_status=models.CharField(max_length=7,choices=MAIL_STATUS,default='NOTSENT')

    @classmethod
    def add_new_mail_summary(cls,email_type,activity_uuid,candidate_name,mail_status):
        MailSummary.objects.create(mail_type=email_type,activity_uuid=activity_uuid,candidate_name=candidate_name,date_of_mail=timezone.now(),mail_status=mail_status)
    

    @classmethod
    def get_latest_mail_sent_date(cls,submission):
        latest_mail_summary=MailSummary.objects.filter(activity_uuid=submission.activity_uuid,mail_status='SENT').latest('date_of_mail')
        latest_mail_sent_date=latest_mail_summary.date_of_mail.date()
        return latest_mail_sent_date
    
    @classmethod
    def get_latest_mail_sent_type(cls,submission):
        latest_mail_summary=MailSummary.objects.filter(activity_uuid=submission.activity_uuid,mail_status='SENT').latest('date_of_mail')
        latest_mail_sent_type=latest_mail_summary.mail_type
        return latest_mail_sent_type
