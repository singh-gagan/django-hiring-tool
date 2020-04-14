import logging

from celery import shared_task
from django.utils import timezone
from django.utils.crypto import get_random_string

from hiringapp.constants import ActivityStatus

from .constants import EmailType
from .mailutils import create_messages, get_mail_service, send_message
from .models import MailSummary

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("mails.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@shared_task
def send_emails(activity_uuid,email_type):
    from hiringapp.models import Submission
    submission=Submission.get_submission(activity_uuid)
    mail_summary=MailSummary.add_new_mail_summary(email_type,activity_uuid,submission.candidate_name,'NOTSENT')
    try:
        message=create_messages(submission,email_type)
        service=get_mail_service(submission.invitation_host)
        sent = send_message(service,'me', message)
        mail_summary.mail_status='SENT'
        mail_summary.save(update_fields=["mail_status",])
        logger.info("{} mail sent. Activity ID - {}".format(email_type,activity_uuid))
    except Exception as e:
        logger.error("{} mail not sent. Activity Id - {}".format(email_type,activity_uuid))
        logger.error('Error while sending {} mail'.format(email_type),exc_info=e)    

@shared_task
def checkout_pending_tasks():
    from hiringapp.models import Submission
    current_date=timezone.now().date()
    reminders_gap_list=[1,3,6]
    all_submissions=Submission.get_all_submission()
    for submission in all_submissions:
        if submission.activity_status == ActivityStatus.NOT_YET_STARTED.value:
           check_for_reminder_to_start_mails(submission,reminders_gap_list)
        elif submission.activity_status == ActivityStatus.STARTED.value:
            check_for_reminder_to_submit_or_expiry_mails(submission)


def check_for_reminder_to_start_mails(submission,reminders_gap_list):
    current_date=timezone.now().date()
    latest_mail_sent_date=MailSummary.get_latest_mail_sent_date(submission)
    if current_date==latest_mail_sent_date:
        return
    gap=current_date-submission.invitation_creation_dateandtime.date()
    if gap.days in reminders_gap_list:
        send_emails.delay(submission.activity_uuid,EmailType.START_REMINDER.value)


def check_for_reminder_to_submit_or_expiry_mails(submission):
    if timezone.now()<=submission.end_time:
        latest_mail_sent_type=MailSummary.get_latest_mail_sent_type(submission)
        if latest_mail_sent_type==EmailType.SUBMISSION_REMINDER.value: 
            return
        activity_reminder_time=submission.end_time-submission.reminder_for_submission_time
        if timezone.now()>=activity_reminder_time:
            send_emails.delay(submission.activity_uuid,EmailType.SUBMISSION_REMINDER.value)
    else:
        submission.activity_status=ActivityStatus.EXPIRED.value
        submission.save(update_fields=["activity_status"])
        send_emails.delay(submission.activity_uuid,EmailType.ACTIVITY_EXPIRED.value)
