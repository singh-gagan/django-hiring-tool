import base64
import logging
from email.mime.text import MIMEText

import pytz
from django.conf import settings
from django.urls import reverse

from .constants import EmailTemplatePlaceholder, EmailType
from .mailservices import GmailServices
from .models import EmailTemplate
from .utils import convert_timedelta_to_string

logger = logging.getLogger(__name__)


class MailUtils:
    @classmethod
    def create_messages(cls, submission, email_type):
        mail = EmailTemplate.get_mail(email_type)

        message = mail.mail_content
        mail_body = cls.create_mail_body(submission, message)
        message = MIMEText(mail_body, "html")

        if (
            email_type == EmailType.ACTIVITY_EXPIRED.value
            or email_type == EmailType.ACTIVITY_SOLUTION.value
        ):
            message["to"] = GmailServices.get_invitation_host_email(
                submission.activity_host
            )
        else:
            message["to"] = submission.candidate_email

        message["subject"] = mail.mail_subject

        return {"raw": base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    @classmethod
    def create_mail_body(cls, submission, message):
        user_time_zone = pytz.timezone(settings.TIME_ZONE)

        mail_body_keywords = {
            EmailTemplatePlaceholder.CANDIDATE_NAME.value: submission.candidate_name,
            EmailTemplatePlaceholder.CANDIDATE_EMAIL.value: submission.candidate_email,
            EmailTemplatePlaceholder.ACTIVITY_DURATION.value: (
                submission.activity_duration
            ),
            EmailTemplatePlaceholder.ACTIVITY_URL.value: (
                settings.HOST.split("//", 1)[1]
                + reverse("submission_invite", args=(submission.activity_uuid,))
            ),
            EmailTemplatePlaceholder.ACTIVITY_START_TIME.value: (
                ""
                if submission.activity_start_time is None
                else submission.activity_start_time.astimezone(user_time_zone).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
            EmailTemplatePlaceholder.ACTIVITY_SOLUTION_LINK.value: (
                submission.activity_solution_link
            ),
            EmailTemplatePlaceholder.ACTIVITY_LEFT_TIME.value: (
                ""
                if submission.activity_left_time is None
                else convert_timedelta_to_string(submission.activity_left_time)
            ),
        }

        mail_body = message.format(**mail_body_keywords)

        return mail_body
