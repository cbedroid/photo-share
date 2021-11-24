from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Main User Model with Authentication"""

    REQUIRED_FIELDS = ["email"]
    pass
