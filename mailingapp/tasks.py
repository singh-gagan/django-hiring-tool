from .mailutils import create_messages
from django.utils.crypto import get_random_string
from .mailutils import get_mail_service,send_message
from celery import shared_task
from hiringapp.constants import ActivityStatus
from .constants import EmailType
from django.utils import timezone
from datetime import datetime,timedelta
from .models import MailSummary
import logging

@shared_task
def send_emails(activity_uuid,email_type):
    from hiringapp.models import Submission
    submission=Submission.get_submission(activity_uuid)
    message=create_messages(submission,email_type)
    service=get_mail_service(submission.invitation_host)
    sent = send_message(service,'me', message)
    if sent:
        MailSummary.add_new_mail_summary(email_type,activity_uuid,submission.candidate_name,'SENT')
    else:
        MailSummary.add_new_mail_summary(email_type,activity_uuid,submission.candidate_name,'NOTSENT')    
    

@shared_task
def checkout_pending_tasks():
    # This schedulded method will iterate for every submission objects and check for pending tasks of sending emails
    # All reminders mail will be sent in accordance with the pattern given in reminders_gap_list[]
    from hiringapp.models import Submission
    current_date=timezone.now().date()
    reminders_gap_list=[1,3,6]
    all_submissions=Submission.objects.all()
    for submission in all_submissions:
        if submission.activity_status == ActivityStatus.NOTYETSTARTED.value:
            latest_mail_sent_date=MailSummary.get_latest_mail_sent_date(submission)
            if current_date==latest_mail_sent_date:
                continue
            gap=current_date-submission.invitation_creation_dateandtime.date()
            if gap.days in reminders_gap_list:
                send_emails.delay(submission.activity_uuid,EmailType.STARTREMINDER.value)
        elif submission.activity_status == ActivityStatus.STARTED.value and timezone.now()<=submission.end_time:
            latest_mail_sent_type=MailSummary.get_latest_mail_sent_type(submission)
            if latest_mail_sent_type==EmailType.SUBMISSIONREMINDER.value: 
                continue
            activity_reminder_time=submission.end_time-submission.reminder_for_submission_time
            if timezone.now()>=activity_reminder_time:
                send_emails.delay(submission.activity_uuid,EmailType.SUBMISSIONREMINDER.value)
        elif submission.activity_status == ActivityStatus.STARTED.value and timezone.now()>submission.end_time:
            submission.activity_status=ActivityStatus.EXPIRED.value
            submission.save(update_fields=["activity_status"])
            send_emails.delay(submission.activity_uuid,EmailType.ACTIVITYEXPIRED.value)
