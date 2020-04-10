from django.shortcuts import render,get_object_or_404,reverse
from django.contrib import admin
from .models import Submission
from django.urls import path
import httplib2
from googleapiclient.discovery import build
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
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
from mailingapp.models import CredentialsModel
from django.views import View
from django.views.generic import TemplateView
from datetime import datetime,date
from django.utils import timezone
from mailingapp.tasks import send_emails
from hiringapp.utils import ActivityStatus
from mailingapp.constants import EmailType
from django.contrib import messages
# Create your views here.

class SubmissionInviteView(View):
    
    #This will run every time whenever the invite link is loaded whether the status is started,not_started,expired,finished
    def get(self,request,activity_uuid):
        submission=Submission.get_submission(activity_uuid)
        if submission is None:
            return render(request,'hiringapp/display_activity.html',{'invalid':True})    
        if submission.activity_start_time is None:
            return render(request,'hiringapp/display_activity.html',{'submission':submission,})
        else:
            return render(request,'hiringapp/display_activity.html',{'submission':submission,'end_time':submission.end_time,})


    #This will only arise when the candidate clicks on start button
    def post(self, request,activity_uuid):
        submission=Submission.get_submission(activity_uuid)
        if submission is None:
            return render(request,'hiringapp/display_activity.html',{'invalid':True})
        if submission.activity_status==ActivityStatus.STARTED.value:
            messages.error(request,"Your activity is already started")
            return HttpResponseRedirect(reverse('submission_invite',args=(submission.activity_uuid,)))
        submission.activity_status=ActivityStatus.STARTED.value
        submission.activity_start_time=timezone.now()
        submission.save(update_fields=["activity_status","activity_start_time",]) 
        return HttpResponseRedirect(reverse('submission_invite',args=(submission.activity_uuid,)))


class SubmitSolutionView(View):

    def post(self,request,activity_uuid):
        input_solution_link = request.POST['solution_link']
        submission=Submission.get_submission(activity_uuid)
        if submission is None:
            return render(request,'hiringapp/display_activity.html',{'invalid':True})
        if submission.activity_status == ActivityStatus.SUBMITTED.value:
            messages.error(request, 'You can submit solution only once.')
            return HttpResponseRedirect(reverse('submission_invite',args=(submission.activity_uuid,)))    
        submission.activity_status=ActivityStatus.SUBMITTED.value
        submission.activity_solution_link=input_solution_link
        submission.save(update_fields=["activity_status","activity_solution_link",])
        send_emails.delay(submission.activity_uuid,EmailType.ACTIVITYSOLUTION.value)
        return HttpResponseRedirect(reverse('submission_invite',args=(submission.activity_uuid,)))
