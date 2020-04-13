from django.db import models
from django.contrib.auth.models import User
from oauth2client.contrib.django_util.models import CredentialsField
from .constants import EmailType
from oauth2client.contrib.django_util.storage import DjangoORMStorage

# Create your models here.

class CredentialsModel(models.Model): 
    id = models.OneToOneField(User, primary_key = True, on_delete = models.CASCADE) 
    credential = CredentialsField() 

    def __str__(self):
        return self.id.get_username()


    @classmethod
    def get_access_token(cls,credential):
      try:
        access_token=credential.access_token
        return access_token
      except:
        return None


    @classmethod
    def get_credentials(cls,user):
        storage = DjangoORMStorage(CredentialsModel, 'id', user, 'credential')
        credential = storage.get()
        return credential    

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
    mail_type=models.CharField(
        max_length=100,
        choices=[(key.value, key.name) for key in EmailType],
        default=EmailType.INVITATION,
    )
    activity_uuid=models.UUIDField(null=True)
    candidate_name=models.CharField(max_length=200)
    date_of_mail=models.DateTimeField(blank=True,null=True)
