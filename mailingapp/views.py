from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views import View
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from hiringapp.models import Submission

from .mailutils import get_auth_return_credentials, get_authorize_url, get_flow
from .models import CredentialsModel


class GmailAuthenticateView(View):
    def post(self,request):
        authorize_url=get_authorize_url(request.user)
        return HttpResponseRedirect(authorize_url)


class GmailAuthCallbackView(View):
    def get(self,request):
        state = bytes(request.GET.get('state'), 'utf8')
        authorization_code=request.GET.get('code')
        credential = get_auth_return_credentials(state,authorization_code,request.user)
        CredentialsModel.add_credentials(request.user,credential)
        return HttpResponseRedirect(Submission.get_admin_change_list_url())
