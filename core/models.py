from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.conf import settings


class Gallery(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to="gallery")
    slug = models.SlugField(blank=False,editable=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.image.url)
        super().save(*args, **kwargs)


    def get_user(self):
        album = self.album_image.first()
        if album:
            return album.user.username
        return ""

    # def get_absolute_url(self):
    #     return reverse("core:album-detail", kwargs={"slug": self.slug})


    def get_download_title(self):
        user = self.get_user()
        app_name = settings.ROOT_URLCONF.split(".")[0].title()
        return f"{app_name}_{self}_by_{user}.jpg"


class Album(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    images = models.ManyToManyField(Gallery, related_name="album_image", blank=True)
    public = models.BooleanField(default=True)
    slug = models.SlugField(blank=False, editable=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        # Dynamically create slugs from album's name
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_images(self):
        if self.images.exists():
            return self.images.get_queryset()

    def get_absolute_url(self):
        return reverse("core:album-detail", kwargs={"slug": self.slug})

    def get_total_images(self):
        images = self.get_images
        if images:
            return images.count()
        return 0

    def __str__(self):
        return self.name
