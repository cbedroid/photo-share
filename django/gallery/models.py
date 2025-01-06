import re

from core.models import PhotoShareBaseModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from PIL import Image
from rest_framework.reverse import reverse as api_reverse

from .enums import GalleryCategory, GalleryCategoryColor
from .managers import GalleryManager, PhotoManager

User = get_user_model()


class Category(PhotoShareBaseModel):
    name = models.CharField(choices=GalleryCategory.choices, default=GalleryCategory.GENERAL, max_length=50)
    label = models.CharField(
        max_length=80,
        choices=GalleryCategoryColor.choices,
        default=GalleryCategoryColor.BLACK_WHITE,
    )
    slug = models.SlugField(blank=False, editable=False, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ("name",)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.get_name_display())
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("gallery:gallery-list") + f"?q={self.slug}"

    def __str__(self):
        return self.get_name_display()


class Tag(models.Model):
    """Hash Tags"""

    name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.name


class Gallery(PhotoShareBaseModel):
    name = models.CharField(max_length=75, validators=[MinLengthValidator(3)], blank=False, null=False)
    user = models.ForeignKey(User, related_name="galleries", on_delete=models.CASCADE)
    public = models.BooleanField(default=True)  # TODO: Update name to `is_public`
    category = models.ForeignKey(
        Category,
        related_name="galleries",
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    slug = models.SlugField(editable=False, db_index=True)

    objects = GalleryManager()

    class Meta:
        ordering = ("-created",)
        unique_together = (
            "name",
            "user",
        )
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @cached_property
    def cover_photo(self) -> str:
        cover_photo = self.photos.filter(is_cover=True).first()
        if cover_photo is not None:
            return cover_photo.image.url
        return static("assets/defaults/default_image.jpg")

    def get_absolute_url(self) -> str:
        return reverse("gallery:gallery-detail", kwargs={"slug": self.slug})

    def get_update_url(self) -> str:
        return reverse("gallery:gallery-update", kwargs={"slug": self.slug})

    def get_delete_url(self) -> str:
        return reverse("gallery:gallery-delete", kwargs={"slug": self.slug})

    def get_api_url(self, request=None) -> str:
        return api_reverse("api:gallery-detail", kwargs={"pk": self.pk}, request=request)

    def __str__(self):
        return self.name


class Photo(PhotoShareBaseModel):
    title = models.CharField(max_length=80, validators=[MinLengthValidator(3)])
    image = models.ImageField(upload_to="gallery")
    gallery = models.ForeignKey(
        Gallery,
        related_name="photos",
        blank=True,
        db_index=True,
        on_delete=models.CASCADE,
    )
    is_cover = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    slug = models.SlugField(blank=False, editable=False, db_index=True)

    objects = PhotoManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("gallery:photo-detail", kwargs={"slug": self.slug})

    def get_update_url(self) -> str:
        return reverse("gallery:photo-update", kwargs={"slug": self.slug})

    def get_transfer_url(self) -> str:
        return reverse("gallery:photo-transfer", kwargs={"pk": self.id})

    def get_delete_url(self) -> str:
        return reverse("gallery:photo-delete", kwargs={"slug": self.slug})

    def get_download_title(self) -> str:
        """Creates filename for download from photo title"""
        user = self.gallery.user
        app_name = settings.ROOT_URLCONF.split(".")[0].title()
        photo = re.sub(" ", "_", str(self))
        return f"{app_name}_{photo}_by_{user}.jpg"

    def mime_type(self) -> str:
        image = Image.open(self.image.path)
        return image.get_format_mimetype() or "unknown"

    def dimension(self) -> str:
        return f"{self.image.height} X {self.image.width}"

    def total_likes(self) -> int:
        return self.rate_set.like.filter(like=True).count()

    def total_stars(self) -> int:
        return self.rate_set.like.filter(star=True).count()


class Rate(PhotoShareBaseModel):
    like = models.BooleanField(default=False)
    star = models.BooleanField(default=False)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} {self.photo.title} - Like: {int(self.like)} Star: {int(self.star)}"
