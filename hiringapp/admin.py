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
from .models import CredentialsModel,MailModel
from django_summernote.admin import SummernoteModelAdmin
from .models import MailModel,MailSummary
from django.utils import timezone
from logging import CRITICAL


admin.site.register(CredentialsModel)
#admin.site.register(MailModel)
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    change_list_template="change_list.html"
    actions = ['cancel_flow',]
    list_display = ('candidate_name','activity_status','invitation_creation_dateandtime','activity_start_time')
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
        extra_context = extra_context or {}
        extra_context['status'] = status
        return super(SubmissionAdmin, self).changelist_view(request, extra_context=extra_context)
   
    def save_model(self, request, obj, form, change):
        if not change:
            obj.invitation_host=request.user
            obj.invitation_creation_dateandtime=timezone.now()
        return super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return CredentialsModel.objects.filter(id=request.user).exists()
        
    def cancel_flow(self,request,queryset):
        for submission in queryset:
            submission.activity_status='expired'
            submission.save()
    cancel_flow.short_description='Cancel process flow'



@admin.register(MailModel)
class MailAdmin(SummernoteModelAdmin):
    summernote_fields=('mail_content',)


@admin.register(MailSummary)
class MailSummary(admin.ModelAdmin):
    list_display = ('candidate_name','mail_type','date_of_mail')
