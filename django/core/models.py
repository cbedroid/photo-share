import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from rest_framework.reverse import reverse as api_reverse


class GalleryManager(models.Manager):
    def query_search(self, query=None, qs=None):
        qs = qs or self.get_queryset()
        if query is not None:
            gallery_lookups = (
                Q(name__icontains=query) | Q(user__username__icontains=query) | Q(category__slug__icontains=query)
            )
            qs = qs.filter(gallery_lookups).distinct()
        return qs


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
        ("bl", "bgc-blue text-white text-light"),
        ("bk", "bgc-black text-white text-light"),
        ("gy", "bgc-grey text-white text-light"),
        ("gn", "bgc-green text-white text-dark"),
        ("yl", "bgc-yellow text-dark text-dark"),
        ("rd", "bgc-red text-white text-light"),
        ("lbl", "bgc-cyan text-white text-light"),
        ("or", "bgc-orange text-white text-light"),
        ("br", "bgc-brown text-white text-light"),
        ("lbr", "bgc-lt-brown text-white text-light"),
        ("pk", "bgc-pink  text-white text-light"),
        ("pr", "bgc-purple  text-white text-light"),
    )
    name = models.IntegerField(choices=CATEGORY_LIST, default=0, db_index=True)
    label = models.CharField(max_length=3, choices=CATEGORY_LABEL, default="gy")
    slug = models.SlugField(blank=False, editable=False, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, commit=True, *args, **kwargs):
        # Dynamically create slugs from Category's name
        self.slug = slugify(self.get_name_display())
        super().save(*args, **kwargs)

    @classmethod
    def choicefield_filter(cls, lookup):
        """Choicefield lookup filter"""
        lookup = str(lookup)
        reverse_dict_category = dict(map(reversed, Category.CATEGORY_LIST))
        value = reverse_dict_category.get(lookup)
        if not lookup.isnumeric():
            lookup = None
        return cls.objects.filter(Q(name=value) | Q(name=lookup))

    def get_absolute_url(self):
        return reverse("core:index") + f"?q={self.slug}"

    def __str__(self):
        return self.get_name_display()


class Tag(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name or "Tags"


class Gallery(models.Model):
    objects = GalleryManager()

    name = models.CharField(max_length=75, validators=[MinLengthValidator(3)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public = models.BooleanField(default=True)
    slug = models.SlugField(blank=False, editable=False, db_index=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, db_index=True)
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

    def cover_photo(self):
        cover = self.photo_set.filter(is_cover=True)
        if cover.exists():
            return cover.first()
        return self.photo_set.first()

    def get_absolute_url(self):
        return reverse(
            "core:gallery-detail",
            kwargs={"slug": self.slug, "owner": slugify(self.user.username)},
        )

    def get_update_url(self):
        return reverse(
            "core:gallery-update",
            kwargs={"slug": self.slug, "owner": slugify(self.user.username)},
        )

    def get_delete_url(self):
        return reverse(
            "core:gallery-delete",
            kwargs={"slug": self.slug, "owner": slugify(self.user.username)},
        )

    def get_api_url(self, request=None):
        return api_reverse("api:gallery-detail", kwargs={"pk": self.slug}, request=request)

    def __str__(self):
        return self.name


class Photo(models.Model):
    title = models.CharField(max_length=75, validators=[MinLengthValidator(3)])
    image = models.ImageField(upload_to="gallery")
    slug = models.SlugField(blank=False, editable=False, db_index=True)
    gallery = models.ForeignKey(Gallery, db_index=True, on_delete=models.CASCADE)
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
        # SlugField should also be deleted,It's only vaild for API lookups
        url = f"{self.title}"
        self.slug = slugify(url)
        self.set_gallery_cover()
        super().save(*args, **kwargs)

    def set_gallery_cover(self):
        # Reset related all photo cover from gallery
        # and set the current photo as the cover
        if self.is_cover:
            photo_set = self.gallery.photo_set.all()
            for photo in photo_set:
                photo.is_cover = False
                # if saved here, there may be a recursive error
            self.is_cover = True  # set the current phoo as the cover

    def get_absolute_url(self):
        return reverse(
            "core:photo-detail",
            kwargs={
                "slug": self.slug,
                "owner": slugify(self.gallery.user.username),
                "gallery": (slugify(self.gallery.name)),
            },
        )

    def get_delete_url(self):
        return reverse("core:photo-delete", kwargs={"pk": self.pk})

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
