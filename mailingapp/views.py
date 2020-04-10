from django.shortcuts import render,get_object_or_404,reverse
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
from mysite import settings
from django.conf.urls import url
from .models import CredentialsModel
from django.views import View
from django.views.generic import TemplateView
from datetime import datetime,date
from django.utils import timezone
from .constants import EmailType
from django.contrib import messages
from .mailutils import get_flow


class GmailAuthenticateView(View):
    def post(self,request):
        storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
        credential = storage.get()
        FLOW=get_flow()
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)


class GmailAuthReturnView(View):
    def get(self,request):
        state = bytes(request.GET.get('state'), 'utf8')
        if not xsrfutil.validate_token(settings.SECRET_KEY, state,
                                      request.user):
            return HttpResponseBadRequest()
        FLOW=get_flow()
        credential = FLOW.step2_exchange(request.GET.get('code'))
        storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
        storage.put(credential)
        #print("access_token: %s" % credential.access_token)
        return HttpResponseRedirect("../admin/hiringapp/submission/")    
