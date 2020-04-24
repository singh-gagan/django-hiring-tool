from unittest.mock import patch

import pytz
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from activitylauncher.models import Invitation
from maildroid.mailutils import MailUtils
from maildroid.utils import convert_timedelta_to_string


class TestMailUtils(TestCase):
    @patch("maildroid.tasks.send_emails.delay")
    def setUp(self, mocked_send_emails):
        self.list_of_placeholders = [
            "{candidate_name}",
            "{candidate_email}",
            "{activity_duration}",
            "{activity_url}",
            "{activity_start_time}",
            "{activity_solution_link}",
            "{activity_left_time}",
        ]
        self.invitation = Invitation.objects.create(
            candidate_name="test_name",
            candidate_email="test@example.com",
            activity_start_time=timezone.now(),
            activity_solution_link="solution_link",
        )

    def test_create_mail_body(self):
        user_time_zone = pytz.timezone(settings.TIME_ZONE)
        message_with_all_placeholders = ""

        for placeholder in self.list_of_placeholders:
            message_with_all_placeholders += placeholder + " "

        message = message_with_all_placeholders

        dict_for_message = {
            "candidate_name": self.invitation.candidate_name,
            "candidate_email": self.invitation.candidate_email,
            "activity_duration": self.invitation.activity_duration,
            "activity_url": settings.HOST.split("//", 1)[1]
            + reverse("submission_invite", args=(self.invitation.activity_uuid,)),
            "activity_start_time": self.invitation.activity_start_time.astimezone(
                user_time_zone
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "activity_solution_link": self.invitation.activity_solution_link,
            "activity_left_time": convert_timedelta_to_string(
                self.invitation.activity_left_time
            ),
        }

        formatted_message = message.format(**dict_for_message)

        returned_message = MailUtils.create_mail_body(
            self.invitation, message_with_all_placeholders
        )

        self.assertTrue(isinstance(returned_message, str))
        self.assertEquals(formatted_message, returned_message)
