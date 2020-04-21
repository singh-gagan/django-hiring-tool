from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views import View

from activitylauncher.constants import ActivityStatus
from mailingapp.constants import EmailType
from mailingapp.tasks import send_emails

from .models import Submission


class SubmissionInviteView(View):

    # This will run every time whenever the invite link is loaded whether the status
    # is started,not_started,expired,finished
    def get(self, request, activity_uuid):
        submission = Submission.get_submission(activity_uuid)

        if submission is None:
            return render(
                request, "activitylauncher/activity_index.html", {"invalid": True}
            )

        if submission.activity_start_time is None:
            return render(
                request,
                "activitylauncher/activity_index.html",
                {"submission": submission},
            )

        else:
            return render(
                request,
                "activitylauncher/activity_index.html",
                {
                    "submission": submission,
                    "activity_end_time": submission.activity_end_time,
                },
            )

    # This will only arise when the candidate clicks on start button
    def post(self, request, activity_uuid):
        submission = Submission.get_submission(activity_uuid)

        if submission is None:
            return render(
                request, "activitylauncher/activity_index.html", {"invalid": True}
            )

        elif submission.activity_start_time is not None:
            messages.error(request, "Activity has already started.")
            return HttpResponseRedirect(
                reverse("submission_invite", args=(submission.activity_uuid,))
            )

        submission.activity_status = ActivityStatus.STARTED.value
        submission.activity_start_time = timezone.now()
        submission.save(update_fields=["activity_status", "activity_start_time"])

        return HttpResponseRedirect(
            reverse("submission_invite", args=(submission.activity_uuid,))
        )


class SubmitSolutionView(View):
    def post(self, request, activity_uuid):
        input_solution_link = request.POST["solution_link"]
        submission = Submission.get_submission(activity_uuid)

        if submission is None:
            return render(
                request, "activitylauncher/activity_index.html", {"invalid": True}
            )

        elif timezone.now() >= submission.activity_end_time:
            messages.error(request, "Solution not submitted.")
            return HttpResponseRedirect(
                reverse("submission_invite", args=(submission.activity_uuid,))
            )

        elif submission.activity_status == ActivityStatus.SUBMITTED.value:
            messages.error(request, "Solution not submitted.")
            return HttpResponseRedirect(
                reverse("submission_invite", args=(submission.activity_uuid,))
            )

        submission.activity_status = ActivityStatus.SUBMITTED.value
        submission.activity_solution_link = input_solution_link
        submission.save(update_fields=["activity_status", "activity_solution_link"])

        send_emails.delay(submission.activity_uuid, EmailType.ACTIVITY_SOLUTION.value)

        return HttpResponseRedirect(
            reverse("submission_invite", args=(submission.activity_uuid,))
        )
