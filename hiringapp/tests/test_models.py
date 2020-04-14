import uuid
from unittest.mock import patch

from django.test import Client, TestCase

from hiringapp.models import Submission


class TestModels(TestCase):


    @patch('mailingapp.tasks.send_emails.delay')   
    def test_invitation_mail_generated_on_first_time_save(self,mocked_send_emails):
        Submission.objects.create(
            candidate_name="test_name",
            candidate_email="test_email@example.com",
            activity_drive_link="https://example-url.com/",
        )
        self.assertEqual(mocked_send_emails.call_count,1)


    @patch('mailingapp.tasks.send_emails.delay')
    def test_get_submission(self,mocked_send_emails):
        submission=Submission.get_submission(uuid.uuid4())
        self.assertEquals(submission,None)
        submission=Submission.objects.create()
        self.assertIsNotNone(submission)
