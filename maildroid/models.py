from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from oauth2client.contrib.django_util.models import CredentialsField
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from .constants import EmailType, EmailStatus


class GmailCredential(models.Model):
    id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    credential = CredentialsField()

    def __str__(self):
        return self.id.get_username()

    @classmethod
    def has_credentials(cls, user):
        return GmailCredential.objects.filter(id=user).exists()

    @classmethod
    def get_credentials(cls, user):
        storage = DjangoORMStorage(GmailCredential, "id", user, "credential")
        credential = storage.get()
        return credential

    @classmethod
    def add_credentials(cls, user, credential):
        storage = DjangoORMStorage(GmailCredential, "id", user, "credential")
        storage.put(credential)


class EmailTemplate(models.Model):
    mail_type = models.CharField(
        max_length=100,
        choices=[(key.value, key.name) for key in EmailType],
        unique=True,
        default=EmailType.INVITATION,
    )
    mail_subject = models.CharField(max_length=100)
    mail_content = models.CharField(max_length=1000)

    def __str__(self):
        return self.mail_type

    @classmethod
    def get_mail(cls, email_type):
        return EmailTemplate.objects.get(mail_type=email_type)


class EmailLog(models.Model):

    mail_status = models.CharField(
        max_length=100,
        choices=[(key.value, key.name) for key in EmailStatus],
        default=EmailStatus.NOT_SENT,
    )
    mail_type = models.CharField(
        max_length=100,
        choices=[(key.value, key.name) for key in EmailType],
        default=EmailType.INVITATION,
    )
    activity_uuid = models.UUIDField(null=True)
    candidate_name = models.CharField(max_length=200)
    date_of_mail = models.DateTimeField(blank=True, null=True)
    message_id = models.CharField(max_length=200, null=True)

    @classmethod
    def add_new_email_log(cls, email_type, activity_uuid, candidate_name, mail_status):
        email_log = EmailLog.objects.create(
            mail_type=email_type,
            activity_uuid=activity_uuid,
            candidate_name=candidate_name,
            date_of_mail=timezone.now(),
            mail_status=mail_status,
        )

        return email_log

    @classmethod
    def get_latest_mail_sent_date(cls, submission):
        try:
            latest_email_log = EmailLog.objects.filter(
                activity_uuid=submission.activity_uuid,
                mail_status=EmailStatus.SENT.value,
            ).latest("date_of_mail")
        except EmailLog.DoesNotExist:
            return None

        return latest_email_log.date_of_mail.date()

    @classmethod
    def get_latest_mail_sent_type(cls, submission):
        try:
            latest_email_log = EmailLog.objects.filter(
                activity_uuid=submission.activity_uuid,
                mail_status=EmailStatus.SENT.value,
            ).latest("date_of_mail")

            return latest_email_log.mail_type

        except EmailLog.DoesNotExist:
            return None
