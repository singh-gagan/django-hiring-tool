from django.test import TestCase
from django.utils import timezone

from hiringapp.models import Submission
from mailingapp.mailutils import MailUtils


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
        message_with_all_placeholders = ""

        for placeholder in self.list_of_placeholders:
            message_with_all_placeholders += placeholder + " "

        message = MailUtils.create_mail_body(
            self.submission, message_with_all_placeholders
        )
        self.assertTrue(isinstance(message, str))
