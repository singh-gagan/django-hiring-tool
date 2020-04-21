import pytz
from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from activitylauncher.models import Submission
from maildroid.mailutils import MailUtils
from maildroid.utils import convert_timedelta_to_string


class TestMailUtils(TestCase):
    def setUp(self):
        self.list_of_placeholders = [
            "{candidate_name}",
            "{candidate_email}",
            "{activity_duration}",
            "{activity_url}",
            "{activity_start_time}",
            "{activity_solution_link}",
            "{activity_left_time}",
        ]
        self.submission = Submission.objects.create(
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
            "candidate_name": self.submission.candidate_name,
            "candidate_email": self.submission.candidate_email,
            "activity_duration": self.submission.activity_duration,
            "activity_url": settings.HOST.split("//", 1)[1]
            + reverse("submission_invite", args=(self.submission.activity_uuid,)),
            "activity_start_time": self.submission.activity_start_time.astimezone(
                user_time_zone
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "activity_solution_link": self.submission.activity_solution_link,
            "activity_left_time": convert_timedelta_to_string(
                self.submission.activity_left_time
            ),
        }

        formatted_message = message.format(**dict_for_message)

        returned_message = MailUtils.create_mail_body(
            self.submission, message_with_all_placeholders
        )

        self.assertTrue(isinstance(returned_message, str))
        self.assertEquals(formatted_message, returned_message)
