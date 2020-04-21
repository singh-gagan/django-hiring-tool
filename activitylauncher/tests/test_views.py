import uuid
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from activitylauncher.constants import ActivityStatus
from activitylauncher.models import Submission


class TestViews(TestCase):
    @patch("maildroid.tasks.send_emails.delay")
    def setUp(self, mocked_send_emails):
        self.client = Client()

        self.submission_invite_url_with_random_uuid = reverse(
            "submission_invite", args=(uuid.uuid4(),)
        )
        self.submission_solution_url_with_random_uuid = reverse(
            "submission_solution", args=(uuid.uuid4(),)
        )

        self.submission = Submission.objects.create()
        self.submission_invite_url_with_valid_uuid = reverse(
            "submission_invite", args=(self.submission.activity_uuid,)
        )
        self.submission_solution_url_with_valid_uuid = reverse(
            "submission_solution", args=(self.submission.activity_uuid,)
        )

    def test_submission_invite_GET(self):
        response = self.client.get(self.submission_invite_url_with_random_uuid)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "activitylauncher/activity_index.html")

    @patch("maildroid.tasks.send_emails.delay")
    def test_submission_invite_with_radom_uuid_POST(self, mocked_send_emails):
        response = self.client.post(self.submission_invite_url_with_random_uuid)

        self.assertEquals(response.status_code, 200)

    @patch("maildroid.tasks.send_emails.delay")
    def test_submission_invite_with_valid_uuid_POST(self, mocked_send_emails):
        response = self.client.post(self.submission_invite_url_with_valid_uuid)
        self.submission.refresh_from_db()

        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.submission.activity_status, ActivityStatus.STARTED.value)

    def test_submission_solution_with_random_uuid_POST(self):
        response = self.client.post(
            self.submission_solution_url_with_random_uuid, {"solution_link": "link"}
        )

        self.assertEquals(response.status_code, 200)

    @patch("maildroid.tasks.send_emails.delay")
    def test_submission_solution_with_valid_uuid_POST(self, mocked_send_emails):
        self.submission.activity_status = ActivityStatus.STARTED.value
        self.submission.activity_start_time = timezone.now()
        self.submission.save()

        response = self.client.post(
            self.submission_solution_url_with_valid_uuid, {"solution_link": "link"}
        )
        self.submission.refresh_from_db()

        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            self.submission.activity_status, ActivityStatus.SUBMITTED.value
        )