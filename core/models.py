from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User


class DateTime(models.Model):
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)


class Gallery(models.Model):
    title = models.CharField(max_length=75, blank=True)
    image = models.ImageField(upload_to="gallery")
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title


class Album(DateTime):
    name = models.CharField(max_length=80)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    images = models.ManyToManyField(Gallery, related_name="album_image")
    public = models.BooleanField(default=True)
    slug = models.SlugField(blank=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        # Dynamically create slugs from album's name
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_images(self):
        if self.images.exists():
            return self.images.get_queryset()

    def get_absolute_url(self):
        return reverse("core:album-detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name
