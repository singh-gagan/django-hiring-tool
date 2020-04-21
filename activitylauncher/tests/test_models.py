import uuid
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from activitylauncher.models import Submission


class TestModels(TestCase):
    @patch("maildroid.tasks.send_emails.delay")
    def test_invitation_mail_generated_on_first_time_save(self, mocked_send_emails):
        Submission.objects.create()
        self.assertEqual(mocked_send_emails.call_count, 1)

    @patch("maildroid.tasks.send_emails.delay")
    def test_get_submission(self, mocked_send_emails):
        submission = Submission.get_submission(uuid.uuid4())
        self.assertEquals(submission, None)

        submission = Submission.objects.create()
        self.assertIsNotNone(submission)

    def test_activity_end_time_property(self):
        submission = Submission.objects.create()
        end_time_without_starting_activity = submission.activity_end_time
        self.assertEquals(None, end_time_without_starting_activity)
        submission.activity_start_time = timezone.now()
        submission.save()
        end_time_after_starting_activity = (
            submission.activity_start_time + submission.activity_duration
        )
        self.assertEquals(
            end_time_after_starting_activity, submission.activity_end_time
        )

    def test_activity_left_time_property(self):
        submission = Submission.objects.create()
        self.assertEquals(None, submission.activity_end_time)
        submission.activity_start_time = timezone.now()
        submission.save()
        left_time_after_starting = submission.activity_end_time - timezone.now()
        self.assertEquals(left_time_after_starting, submission.activity_left_time)
