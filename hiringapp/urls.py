from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns=[
    path('admin/',admin.site.urls),
    path('authenticate/',views.Gmail_Authenticate.as_view(),name='gmail_authenticate'),
    path('admin/oauth2callback',views.Auth_Return.as_view(),name='oauth2callback'),
    path('logout/',views.Log_Out.as_view(),name='log_out'),
    path('submission_invite/(?P<factory_id>[0-9a-f-]+)',views.SubmissionInvite.as_view(),name='submission_invite'),
    #path('display_activity/(?P<factory_id>[0-9a-f-]+)',views.SubmissionInvite.as_view(),name='display_activity'),
]