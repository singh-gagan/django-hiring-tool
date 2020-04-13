from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import MailModel,CredentialsModel,MailSummary
# Register your models here.

@admin.register(MailModel)
class MailAdmin(SummernoteModelAdmin):
    summernote_fields=('mail_content',)


@admin.register(MailSummary)
class MailSummary(admin.ModelAdmin):
    list_display = ('candidate_name','mail_type','date_of_mail','mail_status')


@admin.register(CredentialsModel)
class CredentialsAdmin(admin.ModelAdmin): 
    pass
