from django.urls import resolve, reverse

from mailingapp.views import GmailAuthCallbackView, GmailAuthenticateView


def test_authenticate_url_resolved(self):
        url = reverse('gmail_authenticate')
        self.assertEqual(resolve(url).func.view_class, GmailAuthenticateView)

def test_oauth2callback_url_resolved(self):
        url = reverse('oauth2callback')
        self.assertEqual(resolve(url).func.view_class, GmailAuthCallbackView)
