from django.test import TestCase
from django.urls import reverse, resolve
import uuid
from hiringapp.views import*


class TestUrls(TestCase):
    def test_submission_invite_url_resolved(self):
        url = reverse('submission_invite', args=(uuid.uuid4(),))
        self.assertEqual(resolve(url).func.view_class, SubmissionInvite)

    def test_submission_solution_url_resolved(self):
        url = reverse('submission_solution', args=(uuid.uuid4(),))
        self.assertEqual(resolve(url).func.view_class, SubmitSolution)

    def test_authenticate_url_resolved(self):
        url = reverse('gmail_authenticate')
        self.assertEqual(resolve(url).func.view_class, Gmail_Authenticate)

    def test_oauth2callback_url_resolved(self):
        url = reverse('oauth2callback')
        self.assertEqual(resolve(url).func.view_class, Auth_Return)

    def test_log_out_url_resolved(self):
        url = reverse('log_out')
        self.assertEqual(resolve(url).func.view_class, Log_Out)
