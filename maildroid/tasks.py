import logging

from celery import shared_task
from django.utils import timezone

from activitylauncher.constants import ActivityStatus

from .constants import EmailType
from .mailservices import GmailServices
from .mailutils import MailUtils
from .models import EmailLog, EmailStatus

logger = logging.getLogger(__name__)


@shared_task
def send_emails(activity_uuid, email_type):
    from activitylauncher.models import Submission

    logger.info(
        "Sending {email_type} email. Actiivty UUID-{activity_uuid}".format(
            email_type=email_type, activity_uuid=activity_uuid
        )
    )

    submission = Submission.get_submission(activity_uuid)
    email_log = EmailLog.add_new_email_log(
        email_type, activity_uuid, submission.candidate_name, EmailStatus.NOT_SENT.value
    )

    try:
        message = MailUtils.create_messages(submission, email_type)
    except IndexError as error:
        logger.error(
            "{} email not sent. Activity UUID - {}".format(email_type, activity_uuid),
            exc_info=error,
        )
        return

    sent_message = GmailServices.send_message(submission.invitation_host, message)
    if sent_message is not None:
        email_log.mail_status = EmailStatus.SENT.value
        email_log.message_id = sent_message["id"]
        email_log.save(update_fields=["mail_status", "message_id"])
        logger.info(
            "{} email sent. Activity UUID - {}".format(email_type, activity_uuid)
        )
    else:
        logger.error(
            "{} email not sent. Activity UUID - {}".format(email_type, activity_uuid)
        )


@shared_task
def checkout_pending_tasks():
    from activitylauncher.models import Submission

    all_submissions = Submission.get_all_submission()
    for submission in all_submissions:
        if submission.activity_status == ActivityStatus.NOT_YET_STARTED.value:
            send_reminder_to_start_email.delay(submission.activity_uuid)
        elif submission.activity_status == ActivityStatus.STARTED.value:
            if timezone.now() <= submission.activity_end_time:
                send_reminder_to_submit_email.delay(submission.activity_uuid)
            else:
                send_activity_expired_email.delay(submission.activity_uuid)


@shared_task
def send_reminder_to_start_email(activity_uuid):
    from activitylauncher.models import Submission

    submission = Submission.get_submission(activity_uuid)
    reminders_gap_list = [1, 3, 6]
    current_date = timezone.now().date()
    latest_mail_sent_date = EmailLog.get_latest_mail_sent_date(submission)
    if latest_mail_sent_date is None:
        return
    if current_date == latest_mail_sent_date:
        return

    gap = current_date - submission.invitation_creation_dateandtime.date()
    if gap.days in reminders_gap_list:
        send_emails.delay(submission.activity_uuid, EmailType.START_REMINDER.value)


@shared_task
def send_reminder_to_submit_email(activity_uuid):
    from activitylauncher.models import Submission

    submission = Submission.get_submission(activity_uuid)
    latest_mail_sent_type = EmailLog.get_latest_mail_sent_type(submission)
    if latest_mail_sent_type is None:
        return
    if latest_mail_sent_type == EmailType.SUBMISSION_REMINDER.value:
        return

    activity_reminder_time = (
        submission.activity_end_time - submission.reminder_for_submission_time
    )
    if timezone.now() >= activity_reminder_time:
        send_emails.delay(submission.activity_uuid, EmailType.SUBMISSION_REMINDER.value)


@shared_task
def send_activity_expired_email(activity_uuid):
    from activitylauncher.models import Submission

    submission = Submission.get_submission(activity_uuid)
    submission.activity_status = ActivityStatus.EXPIRED.value
    submission.save(update_fields=["activity_status"])
    send_emails.delay(submission.activity_uuid, EmailType.ACTIVITY_EXPIRED.value)