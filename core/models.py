import re
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.conf import settings


class Gallery(models.Model):
    name = models.CharField(max_length=75)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public = models.BooleanField(default=True)
    slug = models.SlugField(blank=False, editable=False, db_index=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ["-created"]
        unique_together = ["name", "user"]
        verbose_name_plural = "Galleries"

    def save(self, commit=True, *args, **kwargs):
        # Dynamically create slugs from Gallery's name
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def default_cover(self):
        return settings.MEDIA_URL + "gallery/default_image.png"

    def get_absolute_url(self):
        return reverse(
            "core:gallery-detail",
            kwargs={"slug": self.slug, "owner": slugify(self.user.username)},
        )

    def __str__(self):
        return self.name


class Photo(models.Model):
    title = models.CharField(max_length=75)
    image = models.ImageField(upload_to="gallery")
    slug = models.SlugField(blank=False, editable=False, db_index=True)
    gallery = models.ForeignKey(Gallery, db_index=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # This whole method can be deleted.
        # SlugField should also be deleted,It's only vaild for API lookups
        url = f"{self.title}"
        self.slug = slugify(url)
        super().save(*args, **kwargs)

    def get_download_title(self):
        user = self.gallery.user
        app_name = settings.ROOT_URLCONF.split(".")[0].title()
        return f"{app_name}_{self}_by_{user}.jpg"
