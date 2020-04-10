from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from mailingapp import views as mailingapp_views

urlpatterns = [
    path('authenticate/', mailingapp_views.GmailAuthenticateView.as_view(),
         name='gmail_authenticate'),
    path('oauth2callback', mailingapp_views.GmailAuthReturnView.as_view(), name='oauth2callback'),
    re_path('submission_invite/(?P<activity_uuid>[0-9a-f-]+)',
            views.SubmissionInviteView.as_view(), name='submission_invite'),
    re_path('submission_solution/(?P<activity_uuid>[0-9a-f-]+)',
            views.SubmitSolutionView.as_view(), name='submission_solution'),
]
