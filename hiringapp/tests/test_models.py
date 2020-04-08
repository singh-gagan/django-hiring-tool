from django.test import TestCase, Client
from hiringapp.models import Submission
from unittest.mock import patch

class TestModels(TestCase):


    @patch('hiringapp.tasks.send_emails.delay')   
    def test_invitation_mail_generated_on_first_time_save(self,mocked_send_emails):
        Submission.objects.create(
            candidate_name="test_name",
            candidate_email="test_email@example.com",
            activity_drive_link="https://example-url.com/",
        )
        self.assertEqual(mocked_send_emails.call_count,1)

