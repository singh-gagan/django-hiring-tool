import uuid
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from activitylauncher.models import Invitation


class TestModels(TestCase):
    @patch("maildroid.tasks.send_emails.delay")
    def test_invitation_mail_generated_on_first_time_save(self, mocked_send_emails):
        Invitation.objects.create()
        self.assertEqual(mocked_send_emails.call_count, 1)

    @patch("maildroid.tasks.send_emails.delay")
    def test_get_invitation(self, mocked_send_emails):
        invitation = Invitation.get_invitation(uuid.uuid4())
        self.assertEquals(invitation, None)

        invitation = Invitation.objects.create()
        self.assertIsNotNone(invitation)

    @patch("maildroid.tasks.send_emails.delay")
    def test_activity_end_time_property(self, mocked_send_emails):
        invitation = Invitation.objects.create()
        end_time_without_starting_activity = invitation.activity_end_time
        self.assertEquals(None, end_time_without_starting_activity)
        invitation.activity_start_time = timezone.now()
        invitation.save()
        end_time_after_starting_activity = (
            invitation.activity_start_time + invitation.activity_duration
        )
        self.assertEquals(
            end_time_after_starting_activity, invitation.activity_end_time
        )

    @patch("maildroid.tasks.send_emails.delay")
    def test_activity_left_time_property(self, mocked_send_emails):
        invitation = Invitation.objects.create()
        self.assertEquals(None, invitation.activity_end_time)
        invitation.activity_start_time = timezone.now()
        invitation.save()
        left_time_after_starting = invitation.activity_end_time - timezone.now()
        self.assertEquals(left_time_after_starting, invitation.activity_left_time)
