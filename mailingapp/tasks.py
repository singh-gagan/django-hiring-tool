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
    submission=Submission.objects.get(activity_uuid=activity_uuid)
    try:
        message=create_messages(submission,email_type)
        service=get_mail_service(submission.invitation_host)
        sent = send_message(service,'me', message)
        MailSummary.objects.create(mail_type=email_type,activity_uuid=activity_uuid,candidate_name=submission.candidate_name,date_of_mail=timezone.now()) 
        logging.info('{} mail sent for activity uuid {}'.format(email_type,activity_uuid))    
    except:
        logging.error('Mail not sent')


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
            latest_mail_summary=MailSummary.objects.filter(activity_uuid=submission.activity_uuid).latest('date_of_mail')
            latest_mail_sent_date=latest_mail_summary.date_of_mail.date()
            if current_date==latest_mail_sent_date:
                continue
            gap=current_date-submission.invitation_creation_dateandtime.date()
            if gap.days in reminders_gap_list:
                send_emails.delay(submission.activity_uuid,EmailType.STARTREMINDER.value)
        elif submission.activity_status == ActivityStatus.STARTED.value and submission.activity_start_time+submission.activity_duration >= timezone.now():
            latest_mail_summary=MailSummary.objects.filter(activity_uuid=submission.activity_uuid).latest('date_of_mail')
            if latest_mail_summary.mail_type==EmailType.SUBMISSIONREMINDER.value: 
                continue
            activity_end_time=submission.activity_start_time+submission.activity_duration
            activity_reminder_time=activity_end_time-submission.reminder_for_submission_time
            if timezone.now()>=activity_reminder_time:
                send_emails.delay(submission.activity_uuid,EmailType.SUBMISSIONREMINDER.value)
        elif submission.activity_status == ActivityStatus.STARTED.value and submission.activity_start_time+submission.activity_duration < timezone.now():
            submission.activity_status=ActivityStatus.EXPIRED.value
            submission.save()
            send_emails.delay(submission.activity_uuid,EmailType.ACTIVITYEXPIRED.value)

