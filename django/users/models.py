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
        google_account = self.socialaccount_set.filter(provider="google")
        default_image = static("assets/defaults/default_user.jpg")
        if getattr(self, "image", None):
            return self.image.url
        elif google_account.exists():
            google_account = google_account.first()
            image = google_account.extra_data.get("picture", default_image)
            return image

        return default_image

    def get_update_url(self):
        return reverse("user:user-update", kwargs={"slug": self.slug})

    def get_account_delete_url(self):
        return reverse("user:user-delete", kwargs={"slug": self.slug})
