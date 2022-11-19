import datetime
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from maildroid.constants import EmailType
from maildroid.tasks import send_emails

from .constants import ActivityStatus


class Invitation(models.Model):

    # Candidate's related Info
    candidate_name = models.CharField(max_length=50)
    candidate_email = models.EmailField(max_length=70)

    # Activity Realted Info
    activity_duration = models.DurationField(
        default=datetime.timedelta(days=2, hours=0),
        help_text="Use the following format DD HH:MM:SS ",
    )
    activity_start_time = models.DateTimeField(blank=True, null=True, editable=False)
    activity_drive_link = models.URLField(
        max_length=500,
        blank=False,
        help_text="Under the file menu in google doc click Publish to the web and "
        + "copy the iframe link and paste here.",
    )
    activity_uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    activity_solution_link = models.URLField(
        max_length=500, blank=True, null=True, editable=False
    )
    activity_status = models.CharField(
        max_length=500,
        choices=[(key.value, key.name) for key in ActivityStatus],
        default=ActivityStatus.NOT_YET_STARTED.value,
        editable=False,
    )

    # remainder mails related Info
    reminder_for_submission_time = models.DurationField(
        default=datetime.timedelta(days=0, hours=2),
        help_text=(
            "Candidate will be reminded to submit when this much time is left."
            "Enter the time in HH:MM:SS format"
        ),
    )

    # Invitation realted Info who and when
    invitation_host = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=True, null=True
    )
    invitation_creation_dateandtime = models.DateTimeField(
        editable=False, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            send_emails.delay(self.activity_uuid, EmailType.INVITATION.value)

        super(Invitation, self).save(*args, **kwargs)

    def __str__(self):
        str = "Invitation {}".format(self.candidate_name)
        return str

    @classmethod
    def get_invitation(cls, activity_uuid):
        try:
            return Invitation.objects.get(activity_uuid=activity_uuid)
        except Invitation.DoesNotExist:
            return None

    @property
    def activity_end_time(self):
        return (
            None
            if self.activity_start_time is None
            else (self.activity_start_time + self.activity_duration)
        )

    @property
    def activity_left_time(self):
        return (
            None
            if self.activity_end_time is None
            else (self.activity_end_time - timezone.now())
        )

    @classmethod
    def get_admin_change_list_url(cls):
        app_name = (Invitation._meta.app_label).lower()
        class_name = (cls.__name__).lower()
        return reverse("admin:" + app_name + "_" + class_name + "_" + "changelist")

    @classmethod
    def get_all_invitation(cls):
        return Invitation.objects.all()
