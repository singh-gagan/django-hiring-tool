from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import EmailLog, EmailTemplate, GmailCredential

# Register your models here.

@admin.register(EmailTemplate)
class EmailAdmin(SummernoteModelAdmin):
    summernote_fields=('mail_content',)


@admin.register(EmailLog)
class EmailLog(admin.ModelAdmin):
    list_display = ('candidate_name','mail_type','date_of_mail','mail_status','message_id')


@admin.register(GmailCredential)
class GmailCredentialsAdmin(admin.ModelAdmin): 
    pass
