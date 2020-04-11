from django.contrib import admin
from .models import Submission
import httplib2
from django.http import HttpResponseRedirect
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from httplib2 import Http
from mailingapp.models import CredentialsModel,MailModel,MailSummary
from django.utils import timezone
from .constants import ActivityStatus
import requests
from mailingapp.mailutils import authenticate


#admin.site.register(MailModel)
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    change_list_template="change_list.html"
    actions = ['cancel_flow',]
    list_display = ('candidate_name','activity_status','invitation_creation_dateandtime','activity_start_time')
    def changelist_view(self, request, extra_context=None):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('admin')
        authorized=authenticate(request.user)
        extra_context = extra_context or {}
        extra_context['authorized'] = authorized
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
            submission.activity_status=ActivityStatus.EXPIRED.value
            submission.save()
    cancel_flow.short_description='Cancel process flow'
