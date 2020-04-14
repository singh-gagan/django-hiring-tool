from django.contrib import admin
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('authenticate/', views.GmailAuthenticateView.as_view(),
         name='gmail_authenticate'),
    path('oauth2callback', views.GmailAuthCallbackView.as_view(), name='oauth2callback'),
]
