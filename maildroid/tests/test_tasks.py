import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from activitylauncher.constants import ActivityStatus
from activitylauncher.models import Submission
from maildroid.models import EmailLog
from maildroid.tasks import checkout_pending_tasks
from maildroid.constants import EmailStatus, EmailType


class TestTasks(TestCase):
    def setUp(self):
        settings.CELERY_TASK_ALWAYS_EAGER = True

    @patch("maildroid.tasks.send_emails.delay")
    def test_checkout_pending_task_to_send_reminders_to_start_mails(
        self, mocked_send_emails
    ):
        # Creating invitation objects having gap of 1-7 days between
        # invitation creation datetime and today's date.
        # Given gap pattern is [1,3,6] so out of these 6 objects created
        # only 3 objects are eligible for reminders to start the activity.

        uuid_list_to_send_reminders = []
        for day in range(1, 7):
            invitation = Submission.objects.create(
                invitation_creation_dateandtime=timezone.now()
                - datetime.timedelta(days=day)
            )

            if day == 1 or day == 3 or day == 6:
                uuid_list_to_send_reminders.append(invitation.activity_uuid)

            EmailLog.objects.create(
                activity_uuid=invitation.activity_uuid,
                date_of_mail=invitation.invitation_creation_dateandtime,
                mail_status=EmailStatus.SENT.value,
            )

        # 6 invitaion mails after creating invitation objects
        self.assertEqual(mocked_send_emails.call_count, 6)

        # 3 more reminders to start should be send for the submission
        # who are in the gap of 1,3 and 6
        checkout_pending_tasks.apply()

        uuid_list_to_whom_reminders_were_sent = []
        for call in mocked_send_emails.call_args_list:
            args, kwargs = call
            if args[1] == EmailType.START_REMINDER.value:
                uuid_list_to_whom_reminders_were_sent.append(args[0])

        self.assertEqual(mocked_send_emails.call_count, 9)
        self.assertEqual(
            True, uuid_list_to_send_reminders == uuid_list_to_whom_reminders_were_sent
        )

    @patch("maildroid.tasks.send_emails.delay")
    def test_checkout_pending_task_to_send_reminder_to_submit_mails(
        self, mocked_send_emails
    ):
        invitation = Submission.objects.create(
            invitation_creation_dateandtime=timezone.now()
            - datetime.timedelta(days=1, hours=22)
        )
        EmailLog.objects.create(
            activity_uuid=invitation.activity_uuid,
            date_of_mail=invitation.invitation_creation_dateandtime,
            mail_status=EmailStatus.SENT.value,
        )

        invitation.activity_start_time = invitation.invitation_creation_dateandtime
        invitation.activity_status = ActivityStatus.STARTED.value
        invitation.save()

        checkout_pending_tasks.apply()

        self.assertEqual(mocked_send_emails.call_count, 2)

    @patch("maildroid.tasks.send_emails.delay")
    def test_checkout_pending_task_to_send_expiry_mails_to_admin(
        self, mocked_send_emails
    ):
        invitation = Submission.objects.create(
            invitation_creation_dateandtime=timezone.now() - datetime.timedelta(days=2)
        )
        EmailLog.objects.create(
            activity_uuid=invitation.activity_uuid,
            date_of_mail=invitation.invitation_creation_dateandtime,
        )

        invitation.activity_start_time = invitation.invitation_creation_dateandtime
        invitation.activity_status = ActivityStatus.STARTED.value
        invitation.save()

        checkout_pending_tasks.apply()

        invitation.refresh_from_db()

        self.assertEqual(mocked_send_emails.call_count, 2)
        self.assertEqual(invitation.activity_status, ActivityStatus.EXPIRED.value)
