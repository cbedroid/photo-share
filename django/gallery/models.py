import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from rest_framework.reverse import reverse as api_reverse

from .managers import GalleryManager

User = get_user_model()


class Category(models.Model):

    CATEGORY_LIST = (
        (0, "general"),
        (1, "abstract"),
        (2, "adventure"),
        (3, "architectural"),
        (4, "art"),
        (5, "black and white"),
        (6, "business"),
        (7, "candid"),
        (8, "cityscape"),
        (9, "commercial"),
        (10, "composite"),
        (11, "creative"),
        (12, "documentary"),
        (13, "drone"),
        (14, "double-exposure"),
        (15, "editorial"),
        (16, "event"),
        (17, "family"),
        (18, "fashion"),
        (19, "film"),
        (20, "fine art"),
        (21, "food"),
        (22, "golden hour"),
        (23, "holiday"),
        (24, "indoor"),
        (25, "infrared"),
        (26, "landscape"),
        (27, "lifestyle"),
        (28, "long exposure"),
        (29, "musical"),
        (30, "milky way"),
        (31, "minimalist"),
        (32, "newborn"),
        (33, "night"),
        (34, "pet"),
        (35, "portrait"),
        (36, "product"),
        (37, "real estate"),
        (38, "seascape"),
        (39, "social media"),
        (40, "sports"),
        (41, "still-life"),
        (42, "surreal"),
        (43, "street"),
        (44, "time-lapse"),
        (45, "travel"),
        (46, "underwater"),
        (47, "urban exploration"),
        (48, "war"),
        (49, "wedding"),
        (50, "wildlife"),
    )
    CATEGORY_LABEL = (
        ("bgc-blue text-white", "blue & white"),
        ("bgc-black text-white", "black & white"),
        ("bgc-grey text-white", "grey & white"),
        ("bgc-green text-dark", "green & black"),
        ("bgc-yellow text-dark", "yellow & black"),
        ("bgc-red text-white", "red & white"),
        ("bgc-cyan text-white", "light blue & white"),
        ("bgc-orange text-white", "orange & white"),
        ("bgc-brown text-white", "brown & white"),
        ("bgc-lt-brown text-white", "white brown & white"),
        ("bgc-pink text-white", "pink & white"),
        ("bgc-purple text-white", "purple & white"),
    )
    name = models.IntegerField(choices=CATEGORY_LIST, default=0, db_index=True)
    label = models.CharField(max_length=80, choices=CATEGORY_LABEL, default="gy")
    slug = models.SlugField(blank=False, editable=False, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, commit=True, *args, **kwargs):
        self.slug = slugify(self.get_name_display())
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:index") + f"?q={self.slug}"

    @classmethod
    def choicefield_filter(cls, lookup):
        """Choicefield lookup filter"""
        lookup = str(lookup)
        reverse_dict_category = dict(map(reversed, Category.CATEGORY_LIST))
        value = reverse_dict_category.get(lookup)
        if not lookup.isnumeric():
            lookup = None
        return cls.objects.filter(Q(name=value) | Q(name=lookup))

    def __str__(self):
        return self.get_name_display()


class Tag(models.Model):
    """Hash Tags"""

    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name or "Tags"


class Gallery(models.Model):
    objects = GalleryManager()

    name = models.CharField(max_length=75, validators=[MinLengthValidator(3)])
    user = models.ForeignKey(User, related_name="gallery", on_delete=models.CASCADE)
    public = models.BooleanField(default=True)
    slug = models.SlugField(blank=False, editable=False, db_index=True)
    category = models.ForeignKey(Category, related_name="gallery", null=True, on_delete=models.SET_NULL, db_index=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ["-created"]
        unique_together = ["name", "user"]
        verbose_name_plural = "Galleries"

    def save(self, commit=True, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def cover_photo(self):
        if self.photos:
            cover = self.photos.filter(is_cover=True)
            if cover.exists():
                return cover.first().image.url
        return static("assets/defaults/default_image.jpg")

    def get_absolute_url(self):
        return reverse("gallery:gallery-detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("gallery:gallery-update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("gallery:gallery-delete", kwargs={"pk": self.pk})

    def get_api_url(self, request=None):
        return api_reverse("api:gallery-detail", kwargs={"pk": self.pk}, request=request)

    def __str__(self):
        return self.name


class Photo(models.Model):
    title = models.CharField(max_length=80, validators=[MinLengthValidator(3)])
    image = models.ImageField(upload_to="gallery")
    slug = models.SlugField(blank=False, editable=False, db_index=True)
    gallery = models.ForeignKey(
        Gallery, related_name="photos", null=True, blank=True, db_index=True, on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(Tag, blank=True)
    views = models.PositiveIntegerField(default=0)
    is_cover = models.BooleanField(default=False)
    downloads = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # This whole method can be deleted.
        # SlugField should also be deleted,It's only valid for API lookups
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("gallery:photo-detail", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("gallery:photo-delete", kwargs={"pk": self.pk})

    def get_download_title(self):
        user = self.gallery.user
        app_name = settings.ROOT_URLCONF.split(".")[0].title()
        photo = re.sub(" ", "_", str(self))
        return f"{app_name}_{photo}_by_{user}.jpg"

    def mime_type(self):
        image = Image.open(self.image.path)
        return image.get_format_mimetype() or "unknown"

    def dimension(self):
        return f"{self.image.height} X {self.image.width}"

    def total_likes(self):
        return self.rate_set.like.filter(like=True).count()

    def total_stars(self):
        return self.rate_set.like.filter(star=True).count()


class Rate(models.Model):
    like = models.BooleanField(default=False)
    star = models.BooleanField(default=False)
    photo = models.ForeignKey(Photo, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        photo = ""
        if self.photo:
            photo = self.photo.title
        return f"{self.user} {photo} - Like: {int(self.like)} Star: {int(self.star)}"
