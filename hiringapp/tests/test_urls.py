from django.test import TestCase
from django.urls import reverse, resolve
import uuid


class TestUrls(TestCase):
    def test_submission_invite_url_resolved(self):
        url = reverse('submission_invite', args=(uuid.uuid4(),))
        print(resolve(url))

    def test_submission_invite_url_resolved(self):
        url = reverse('submission_invite', args=(uuid.uuid4(),))
        print(resolve(url))
