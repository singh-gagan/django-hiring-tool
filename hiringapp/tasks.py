import string
from .mailutils import create_messages
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .mailutils import get_mail_service, send_message
from celery import shared_task
from . import models
from .utils import EmailType
from django.utils import timezone
from datetime import datetime, timedelta


@shared_task
def send_emails(id, email_type):
    submission = models.Submission.objects.get(activity_uuid=id)
    try:
        message = create_messages(submission, email_type)
        service = get_mail_service(submission.invitation_host)
        sent = send_message(service, 'me', message)
        models.MailSummary.objects.create(mail_type=email_type, activity_uuid=id,
                                          candidate_name=submission.candidate_name, date_of_mail=timezone.now())
        if email_type == "activity_expired" or email_type == "activity_solution":
            print('{} mail sent successfully to {} activity_uuid {}'.format(
                email_type, submission.invitation_host.get_username(), submission.activity_uuid))
        else:
            print('{} mail sent successfully to {} activity_uuid {}'.format(
                email_type, submission.candidate_name, submission.activity_uuid))
    except:
        print('Mail not sent')
    return "celery_task_executed"


@shared_task
def checkout_pending_tasks():
    # This schedulded method will iterate for every submission objects and check for pending tasks of sending emails
    # All reminders mail will be sent in accordance with the pattern given in reminders_gap_list[]
    current_date = datetime.now().date()
    reminders_gap_list = [1, 3, 6]
    all_submissions = models.Submission.objects.all()
    for submission in all_submissions:
        if submission.activity_status == 'not_yet_started':
            latest_mail_summary = models.MailSummary.objects.filter(
                activity_uuid=submission.activity_uuid).latest('date_of_mail')
            latest_mail_sent_date = latest_mail_summary.date_of_mail.date()
            if current_date == latest_mail_sent_date:
                continue
            gap = current_date-submission.invitation_creation_dateandtime.date()
            if gap in reminders_gap_list:
                send_emails.delay(submission.uuid, 'reminder')
        elif submission.activity_status == 'started' and submission.activity_start_time+submission.activity_duration > datetime.now():
            latest_mail_summary = models.MailSummary.objects.filter(
                activity_uuid=submission.activity_uuid).latest('date_of_mail')
            if latest_mail_summary.mail_type == 'reminder_to_submit':
                continue
            activity_end_time = submission.activity_start_time+submission.activity_duration
            activity_reminder_time = activity_end_time - submission.reminder_for_submission_time
            if datetime.now() >= activity_reminder_time:
                send_emails.delay(submission.activity_uuid,
                                  'reminder_to_submit')
        elif submission.activity_status == 'started' and submission.activity_start_time+submission.activity_duration < datetime.now():
            submission.activity_status = "expired"
            submission.save()
            send_emails.delay(submission.activity_uuid, 'activity_expired')

    return "pending tasks executed"
