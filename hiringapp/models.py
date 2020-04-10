from django.db import models
from django.contrib import admin
from .constants import ActivityStatus
from mailingapp.constants import EmailType
import uuid
from django.contrib.auth.models import User 
from oauth2client.contrib.django_util.models import CredentialsField 
from mailingapp.tasks import send_emails
import datetime


class Submission(models.Model):

    #Candidate's related Info
    candidate_name=models.CharField(max_length=200)
    candidate_email=models.EmailField(max_length = 254)

    #Activity Realted Info
    activity_duration=models.DurationField(default=datetime.timedelta(days=2, hours=0))
    activity_start_time=models.DateTimeField(blank=True,null=True,editable=False)
    activity_drive_link= models.URLField(max_length = 500,blank=False)
    activity_uuid= models.UUIDField(primary_key = True, default = uuid.uuid4)
    activity_solution_link= models.URLField(max_length = 500,blank=True,null=True,editable=False)
    activity_status=models.CharField(
        max_length = 500,
        choices=[(key.value, key.name) for key in ActivityStatus],
        default=ActivityStatus.NOTYETSTARTED.value,
    )

    #remainder mails related Info
    reminder_for_submission_time=models.DurationField(default=datetime.timedelta(days=0,hours=2))

    #Invitation realted Info who and when
    invitation_host=models.ForeignKey(User,on_delete=models.CASCADE,editable=False,blank=True,null=True)
    invitation_creation_dateandtime=models.DateTimeField(editable=False,blank=True,null=True)
    

    def save(self, *args, **kwargs): 
        if self._state.adding is True:
            id=self.activity_uuid
            send_emails.delay(id,EmailType.INVITATION.value)
        super(Submission, self).save(*args, **kwargs) 

    def __str__(self):
        str="Invitation {}".format(self.candidate_name)
        return str

    @classmethod
    def get_submission(cls,activity_uuid):
        try:
            submission = Submission.objects.get(activity_uuid=activity_uuid)
        except Submission.DoesNotExist:
            submission=None
        return submission

    @property
    def end_time(self):
        return self.activity_start_time+self.activity_duration
