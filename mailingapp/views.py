from django.http import HttpResponseRedirect
from django.views import View
from hiringapp.models import Submission

from .mailservices import GmailServices
from .models import GmailCredential


class GmailAuthenticateView(View):
    def post(self, request):
        gmail_authorize_url = GmailServices.get_gmail_authorize_url(request.user)
        return HttpResponseRedirect(gmail_authorize_url)


class GmailAuthCallbackView(View):
    def get(self, request):
        state = bytes(request.GET.get("state"), "utf8")
        authorization_code = request.GET.get("code")

        credential = GmailServices.get_gmail_auth_callback_credential(
            state, authorization_code, request.user
        )
        GmailCredential.add_credentials(request.user, credential)

        return HttpResponseRedirect(Submission.get_admin_change_list_url())
