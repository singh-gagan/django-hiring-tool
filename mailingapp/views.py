from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from .models import CredentialsModel
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from django.contrib import messages
from mysite import settings
from .models import CredentialsModel
from django.views import View
from .mailutils import get_flow,get_authorize_url,get_auth_return_credentials
from hiringapp.models import Submission


class GmailAuthenticateView(View):
    def post(self,request):
        authorize_url=get_authorize_url(request.user)
        return HttpResponseRedirect(authorize_url)


class GmailAuthReturnView(View):
    def get(self,request):
        state = bytes(request.GET.get('state'), 'utf8')
        authorization_code=request.GET.get('code')
        credential = get_auth_return_credentials(state,authorization_code,request.user)
        CredentialsModel.add_credentials(request.user,credential)
        return HttpResponseRedirect(Submission.get_admin_change_list_url())
