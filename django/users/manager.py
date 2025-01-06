from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.db.models import Prefetch


class UserQueryset(models.QuerySet):
    pass


class UserManager(BaseUserManager):
    def get_queryset(self):
        social_account_qs = SocialAccount.objects.all()
        return UserQueryset(self.model, using=self._db).prefetch_related(
            "galleries", Prefetch("socialaccount_set", queryset=social_account_qs)
        )
