from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include, re_path
from . import views
from mailingapp import views as mailingapp_views

urlpatterns = [
    url(r'^authenticate/$', mailingapp_views.GmailAuthenticateView.as_view(),
         name='gmail_authenticate'),
    url(r'^oauth2callback/$', mailingapp_views.GmailAuthReturnView.as_view(), name='oauth2callback'),
    url(r'^invite-acivity/(?P<activity_uuid>[0-9a-f-]+)/$',
            views.SubmissionInviteView.as_view(), name='submission_invite'),
    url(r'^solution-activity/(?P<activity_uuid>[0-9a-f-]+)/$',
            views.SubmitSolutionView.as_view(), name='submission_solution'),
]
