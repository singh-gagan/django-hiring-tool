import uuid

from django.test import TestCase
from django.urls import resolve, reverse

from activitylauncher.views import SubmissionInviteView, SubmitSolutionView


class TestUrls(TestCase):
    def test_submission_invite_url_resolved(self):
        url = reverse("submission_invite", args=(uuid.uuid4(),))
        self.assertEqual(resolve(url).func.view_class, SubmissionInviteView)

    def test_submission_solution_url_resolved(self):
        url = reverse("submission_solution", args=(uuid.uuid4(),))
        self.assertEqual(resolve(url).func.view_class, SubmitSolutionView)
