from django.test import TestCase, Client
from hiringapp.models import Submission
import uuid
from mailingapp.models import*
from mailingapp.mailutils import*
import datetime
from unittest.mock import patch
from mailingapp.tasks import checkout_pending_tasks
from hiringapp.constants import ActivityStatus
from django.utils import timezone
class TestMailUtils(TestCase):

    @patch('mailingapp.tasks.send_emails.delay')
    def test_checkout_pending_tas_to_send_reminders_to_start_mails(self,mocked_send_emails):
        # Creating submission objects having gap of 1-7 days between invitation creation datetime and todays date.
        # Given gap pattern is [1,3,6] so out of this 6 objects going to be created 3 objects are eligible for reminders to start the activity
        for day in range(1,7):
            submission = Submission.objects.create(invitation_creation_dateandtime=timezone.now()-datetime.timedelta(days=day))
            MailSummary.objects.create(activity_uuid=submission.activity_uuid,date_of_mail=submission.invitation_creation_dateandtime,mail_status='SENT')        
        
        # 6 invitaion mails after creating submission objects
        self.assertEqual(mocked_send_emails.call_count,6)
        checkout_pending_tasks.apply()
        # 3 more reminders to start which are in the gap of 1,3 and 6
        self.assertEqual(mocked_send_emails.call_count,9)
    
    @patch('mailingapp.tasks.send_emails.delay')
    def test_checkout_pending_task_to_send_reminder_to_submit_mails(self,mocked_send_emails):
        submission=Submission.objects.create(invitation_creation_dateandtime=timezone.now()-datetime.timedelta(days=1,hours=22))
        MailSummary.objects.create(activity_uuid=submission.activity_uuid,date_of_mail=submission.invitation_creation_dateandtime,mail_status='SENT')
        submission.activity_start_time=submission.invitation_creation_dateandtime
        submission.activity_status=ActivityStatus.STARTED.value
        submission.save()
        checkout_pending_tasks.apply()
        self.assertEqual(mocked_send_emails.call_count,2)

    
    @patch('mailingapp.tasks.send_emails.delay')
    def test_checkout_pending_task_to_send_expiry_mails_to_admin(self,mocked_send_emails):
        submission=Submission.objects.create(invitation_creation_dateandtime=timezone.now()-datetime.timedelta(days=2))
        MailSummary.objects.create(activity_uuid=submission.activity_uuid,date_of_mail=submission.invitation_creation_dateandtime)
        submission.activity_start_time=submission.invitation_creation_dateandtime
        submission.activity_status=ActivityStatus.STARTED.value
        submission.save()
        checkout_pending_tasks.apply()
        submission=Submission.get_submission(activity_uuid=submission.activity_uuid)
        self.assertEqual(mocked_send_emails.call_count,2)
        self.assertEqual(submission.activity_status,ActivityStatus.EXPIRED.value)
