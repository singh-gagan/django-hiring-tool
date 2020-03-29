from django.contrib import admin
from django.urls import path
from . import views

urlpatterns=[
    path('admin/',admin.site.urls),
    path('authenticate/',views.gmail_authenticate,name='gmail_authenticate'),
    path('oauth2callback/',views.auth_return,name='oauth2callback'),
    path('logout/',views.log_out,name='log_out'),
]