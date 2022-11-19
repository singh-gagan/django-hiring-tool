from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views import View

from activitylauncher.constants import ActivityStatus, ActivityInstructions
from maildroid.constants import EmailType
from maildroid.tasks import send_emails

from .models import Invitation


class SubmissionInviteView(View):

    # This will run every time whenever the invite link is loaded whether the status
    # is started,not_started,expired,finished
    def get(self, request, activity_uuid):
        invitation = Invitation.get_invitation(activity_uuid)

        if invitation is None:
            return render(
                request, "activitylauncher/activity_index.html", {"invalid": True}
            )

        if invitation.activity_start_time is None:
            return render(
                request,
                "activitylauncher/activity_index.html",
                {
                    "invitation": invitation,
                    "activity_instructions": ActivityInstructions,
                },
            )

        else:
            return render(
                request,
                "activitylauncher/activity_index.html",
                {
                    "invitation": invitation,
                    "activity_end_time": invitation.activity_end_time,
                    "activity_instructions": ActivityInstructions,
                },
            )

    # This will only arise when the candidate clicks on start button
    def post(self, request, activity_uuid):
        invitation = Invitation.get_invitation(activity_uuid)

        if invitation is None:
            return render(
                request, "activitylauncher/activity_index.html", {"invalid": True}
            )

        elif invitation.activity_start_time is not None:
            messages.error(request, "Activity has already started.")
            return HttpResponseRedirect(
                reverse("submission_invite", args=(invitation.activity_uuid,))
            )

        invitation.activity_status = ActivityStatus.STARTED.value
        invitation.activity_start_time = timezone.now()
        invitation.save(update_fields=["activity_status", "activity_start_time"])

        return HttpResponseRedirect(
            reverse("submission_invite", args=(invitation.activity_uuid,))
        )


class SubmitSolutionView(View):
    def post(self, request, activity_uuid):
        input_solution_link = request.POST["solution_link"]
        invitation = Invitation.get_invitation(activity_uuid)

        if invitation is None:
            return render(
                request, "activitylauncher/activity_index.html", {"invalid": True}
            )

        elif timezone.now() >= invitation.activity_end_time:
            messages.error(request, "Solution not submitted.")
            return HttpResponseRedirect(
                reverse("submission_invite", args=(invitation.activity_uuid,))
            )

        elif invitation.activity_status == ActivityStatus.SUBMITTED.value:
            messages.error(request, "Solution not submitted.")
            return HttpResponseRedirect(
                reverse("submission_invite", args=(invitation.activity_uuid,))
            )

        invitation.activity_status = ActivityStatus.SUBMITTED.value
        invitation.activity_solution_link = input_solution_link
        invitation.save(update_fields=["activity_status", "activity_solution_link"])

        send_emails.delay(invitation.activity_uuid, EmailType.ACTIVITY_SOLUTION.value)

        return HttpResponseRedirect(
            reverse("submission_invite", args=(invitation.activity_uuid,))
        )
