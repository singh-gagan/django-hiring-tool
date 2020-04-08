from django.test import TestCase, Client
from hiringapp.models import Submission
import uuid
from hiringapp.models import*
from hiringapp.mailutils import*
import datetime
from unittest.mock import patch
from hiringapp.tasks import checkout_pending_tasks
class TestMailUtils(TestCase):

    @patch('hiringapp.tasks.send_emails.delay')
    def test_reminder_to_start_mails(self,mocked_send_emails):
        # Creating submission objects having gap of 1-7 days between invitation creation datetime and todays date.
        # Given gap pattern is [1,3,6] so out of this 6 objects going to be created 3 objects are eligible for reminders to start the activity
        for day in range(1,7):
            submission = Submission.objects.create(invitation_creation_dateandtime=datetime.datetime.now()-datetime.timedelta(days=day))
            MailSummary.objects.create(activity_uuid=submission.activity_uuid,date_of_mail=submission.invitation_creation_dateandtime)        
        
        # 6 invitaion mails after creating submission objects
        self.assertEqual(mocked_send_emails.call_count,6)
        checkout_pending_tasks.apply()
        self.assertEqual(mocked_send_emails.call_count,9)
        # 3 more reminders to start which are in the gap of 1,3 and 6