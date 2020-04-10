from django.shortcuts import render,reverse
from .models import Submission
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from datetime import datetime,date
from django.utils import timezone
from mailingapp.tasks import send_emails
from hiringapp.constants import ActivityStatus
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
