from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views import View
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from hiringapp.models import Submission

from .mailutils import get_gmail_callback_credential, get_gmail_authorize_url, get_flow
from .models import GmailCredential


class GmailAuthenticateView(View):
    def post(self,request):
        gmail_authorize_url=get_gmail_authorize_url(request.user)
        return HttpResponseRedirect(gmail_authorize_url)


class GmailAuthCallbackView(View):
    def get(self,request):
        state = bytes(request.GET.get('state'), 'utf8')
        authorization_code=request.GET.get('code')
        credential = get_gmail_callback_credential(state,authorization_code,request.user)
        GmailCredential.add_credentials(request.user,credential)
        return HttpResponseRedirect(Submission.get_admin_change_list_url())
