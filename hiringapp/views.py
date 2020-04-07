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
from .utils import FLOW
from mysite import settings
from django.conf.urls import url
from .models import CredentialsModel
from django.views import View
from django.views.generic import TemplateView
from datetime import datetime,date
from django.utils import timezone
from .tasks import send_emails
# Create your views here.

class Gmail_Authenticate(View):
    def post(self,request):
        storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
        credential = storage.get()
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)


class Auth_Return(View):
    def get(self,request):
        get_state = bytes(request.GET.get('state'), 'utf8')
        if not xsrfutil.validate_token(settings.SECRET_KEY, get_state,
                                      request.user):
            return HttpResponseBadRequest()
        credential = FLOW.step2_exchange(request.GET.get('code'))
        storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
        storage.put(credential)
        print("access_token: %s" % credential.access_token)
        return HttpResponseRedirect("../admin/hiringapp/submission/")


class Log_Out(View):
    def post(self,request):
        instance = CredentialsModel.objects.get(id=request.user)
        instance.delete()
        return HttpResponseRedirect("../admin/hiringapp/submission/")    


class SubmissionInvite(View):
    
    #This will run every time whenever the invite link is loaded whether the status is started,not_started,expired,finished
    def get(self,request,activity_uuid):
        if not Submission.objects.filter(activity_uuid=activity_uuid).exists():
            invalid=True
            return render(request,'hiringapp/display_activity.html',{'invalid':invalid})    
        submission=get_object_or_404(Submission,activity_uuid=activity_uuid)
        if submission.activity_start_time is None:
            return render(request,'hiringapp/display_activity.html',{'submission':submission,})
        if submission.activity_start_time is not None:
            end_time=submission.activity_start_time+submission.activity_duration
            return render(request,'hiringapp/display_activity.html',{'submission':submission,'end_time':end_time,})
    
    #This will only arise when the candidate clicks on start button
    def post(self, request,activity_uuid):
        submission=get_object_or_404(Submission,activity_uuid=activity_uuid)
        submission.activity_status="started"
        submission.activity_start_time=datetime.now()
        submission.save()
        return HttpResponseRedirect(reverse('submission_invite',args=(submission.activity_uuid,)))

class SubmitSolution(View):

    def post(self,request,activity_uuid):
        submission=get_object_or_404(Submission,activity_uuid=activity_uuid)
        submission.activity_status="submitted"
        submission.activity_solution_link=request.POST['solution_link']
        submission.save()
        send_emails.delay(submission.activity_uuid,'activity_solution')
        return HttpResponseRedirect(reverse('submission_invite',args=(submission.activity_uuid,)))

        