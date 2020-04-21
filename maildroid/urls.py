from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r"^authenticate/$",
        views.GmailAuthenticateView.as_view(),
        name="gmail_authenticate",
    ),
    url(
        r"^oauth2callback/$",
        views.GmailAuthCallbackView.as_view(),
        name="oauth2callback",
    ),
]
