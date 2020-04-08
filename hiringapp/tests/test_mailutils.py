from django.test import TestCase, Client
from hiringapp.models import Submission,MailModel
from unittest.mock import patch
from hiringapp.utils import EmailType
from hiringapp.mailutils import create_messages

class TestMailUtils(TestCase):
    def setUp(self):
        self.invite_mail_model=MailModel.objects.create(
            mail_type=EmailType.Invitation.value,
            mail_subject="",
            mail_content="",
        )
        self.reminder_mail_model=MailModel.objects.create(
            mail_type=EmailType.Reminder.value,
            mail_subject="",
            mail_content="",
        )
        self.activity_expired_mail_model=MailModel.objects.create(
            mail_type=EmailType.ActivityExpired.value,
            mail_subject="",
            mail_content="",
        )
        self.activity_solution_mail_model=MailModel.objects.create(
            mail_type=EmailType.ActivitySolution.value,
            mail_subject="",
            mail_content="",
        )
        self.reminder_to_submit_mail_model=MailModel.objects.create(
            mail_type=EmailType.SubmissionReminder.value,
            mail_subject="",
            mail_content="",
        )
        self.submission=Submission.objects.create()



    @patch('hiringapp.mailutils.create_mail_body')
    def test_create_message(self,mocked_create_mail_body):
        invitaion_mail=create_messages(self.submission,EmailType.Invitation.value)
        print(invitaion_mail)
