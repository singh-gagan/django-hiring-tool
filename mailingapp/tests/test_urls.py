from mailingapp.views import*
from django.urls import reverse,resolve

def test_authenticate_url_resolved(self):
        url = reverse('gmail_authenticate')
        self.assertEqual(resolve(url).func.view_class, GmailAuthenticateView)

def test_oauth2callback_url_resolved(self):
        url = reverse('oauth2callback')
        self.assertEqual(resolve(url).func.view_class, GmailAuthReturnView)
