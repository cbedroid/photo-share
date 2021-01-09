import re
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.conf import settings


class Gallery(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public = models.BooleanField(default=True)
    slug = models.SlugField(blank=False, editable=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Galleries"

    def save(self, *args, **kwargs):
        # Dynamically create slugs from Gallery's name
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:gallery-detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name

class Photo(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to="gallery")
    slug = models.SlugField(blank=False, editable=False)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        url = f'{self.title}_{self.pk}'
        self.slug = slugify(url)
        super().save(*args, **kwargs)

    def get_download_title(self):
        user = self.gallery.user
        app_name = settings.ROOT_URLCONF.split(".")[0].title()
        return f"{app_name}_{self}_by_{user}.jpg"

