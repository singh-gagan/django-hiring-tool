from django.contrib import admin
from .models import Submission
from django.urls import path
import httplib2
from googleapiclient.discovery import build
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from .models import CredentialsModel
from oauth2client.contrib import xsrfutil
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from django.shortcuts import render,redirect
from httplib2 import Http
from apiclient import errors
from email.mime.text import MIMEText
import base64
from oauth2client import service_account
from django.contrib import messages
from .utils import FLOW
from mysite import settings
from django.conf.urls import url
from .models import CredentialsModel

# Register your models here.
admin.site.register(CredentialsModel)
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    change_list_template="sign_in_button.html"

    def get_urls(self):
        urls=super().get_urls()
        my_urls=[
            path('authenticate/',self.gmail_authenticate),
            path('oauth2callback/',self.auth_return),
            path('logout/',self.log_out),
        ]
        return my_urls+urls
    
    def changelist_view(self, request, extra_context=None):
        status = True
        if not request.user.is_authenticated:
            return HttpResponseRedirect('admin')
        storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
        credential = storage.get()
        try:
            access_token = credential.access_token
            #This is to re-authenticate the user to check if his access_token is still valid
            resp, cont = Http().request("https://www.googleapis.com/auth/gmail.readonly",
                                    headers={'Host': 'www.googleapis.com',
                                            'Authorization': access_token})                                    
        except:
            status = False
            #print('Not Found')
        
        extra_context = extra_context or {}
        extra_context['status'] = status
        
        return super(SubmissionAdmin, self).changelist_view(request, extra_context=extra_context)

    def gmail_authenticate(self,request):
        storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
        credential = storage.get()
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)


    def auth_return(self,request):
        get_state = bytes(request.GET.get('state'), 'utf8')
        if not xsrfutil.validate_token(settings.SECRET_KEY, get_state,
                                      request.user):
            return HttpResponseBadRequest()
        credential = FLOW.step2_exchange(request.GET.get('code'))
        storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
        storage.put(credential)
        print("access_token: %s" % credential.access_token)
        return HttpResponseRedirect("../")


    def log_out(self,request):
        instance = CredentialsModel.objects.get(id=request.user)
        instance.delete()
        return HttpResponseRedirect("../")