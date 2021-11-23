from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def get_signup_redirect_url(self, request):
        return request.user.account.get_update_url()

    def get_email_confirmation_redirect_url(self, request):
        user = request.user
        if user.is_authenticated and not user.account_verified:
            return request.user.account.get_update_url()
        else:
            return request.user.account.get_dashboard_url()
