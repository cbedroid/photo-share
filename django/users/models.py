from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Main User Model with Authentication"""

    REQUIRED_FIELDS = ["email"]
    image = models.ImageField(
        upload_to="users",
        help_text=_("user profile image "),
        blank=True,
        null=True,
    )
    slug = models.SlugField(editable=False)

    def save(self, **kwargs):
        self.slug = slugify(self.username)
        return super().save(**kwargs)

    def get_profile_pic(self):
        if self.image:
            return self.image.url
        return static("assets/defaults/default_user.jpg")

    def get_update_url(self):
        return reverse("user:user-update", kwargs={"slug": self.slug})

    def get_account_delete_url(self):
        return reverse("user:user-delete", kwargs={"slug": self.slug})
