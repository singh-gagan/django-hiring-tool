from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from .models import CredentialsModel
from oauth2client.contrib import xsrfutil
from oauth2client.contrib.django_util.storage import DjangoORMStorage
from django.contrib import messages
from mysite import settings
from .models import CredentialsModel
from django.views import View
from .mailutils import get_flow
from hiringapp.models import Submission


class GmailAuthenticateView(View):
    def post(self,request):
        FLOW=get_flow()
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)


class GmailAuthReturnView(View):
    def get(self,request):
        state = bytes(request.GET.get('state'), 'utf8')
        if not xsrfutil.validate_token(settings.SECRET_KEY, state,
                                      request.user):
            return HttpResponseBadRequest()
        FLOW=get_flow()
        credential = FLOW.step2_exchange(request.GET.get('code'))
        CredentialsModel.add_credentials(request.user,credential)
        return HttpResponseRedirect(Submission.get_admin_change_list_url())
