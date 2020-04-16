from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^activity-invite/(?P<activity_uuid>[0-9a-f-]+)/$',
        views.SubmissionInviteView.as_view(), name='submission_invite'),
    url(r'^activity-solution/(?P<activity_uuid>[0-9a-f-]+)/$',
        views.SubmitSolutionView.as_view(), name='submission_solution'),
]
