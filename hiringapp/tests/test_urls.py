from django.test import SimpleTestCase
from django.urls import reverse, resolve
import uuid

class TestUrls(SimpleTestCase):
    def test_submission_invite_url_resolved(self):
        url=reverse('submission_invite',args=(uuid.uuid4,))
        print(resolve(url))
