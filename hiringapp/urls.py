from django.contrib import admin
from django.urls import path,include,re_path
from . import views

urlpatterns=[
    path('admin/',admin.site.urls),
    path('authenticate/',views.Gmail_Authenticate.as_view(),name='gmail_authenticate'),
    path('admin/oauth2callback',views.Auth_Return.as_view(),name='oauth2callback'),
    path('logout/',views.Log_Out.as_view(),name='log_out'),
    re_path('submission_invite/(?P<activity_uuid>[0-9a-f-]+)',views.SubmissionInvite.as_view(),name='submission_invite'),
    re_path('submission_solution/(?P<activity_uuid>[0-9a-f-]+)',views.SubmitSolution.as_view(),name='submission_solution'),
]