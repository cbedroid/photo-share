from django.contrib import admin
from django.http import HttpRequest

from .models import Category, Gallery, Photo, Rate, Tag


class DateCreatedAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created",
        "updated",
    )


@admin.register(Gallery)
class GalleryAdmin(DateCreatedAdmin):
    select_related = ("category", "user")
    list_display = ("name", "user", "public", "category")

    def get_queryset(self: "GalleryAdmin", request: HttpRequest):
        qs = super().get_queryset(request)
        return qs.select_related("category", "user").all()


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "gallery", "is_cover")

    def get_queryset(self: "PhotoAdmin", request: HttpRequest):
        qs = super().get_queryset(request)
        return qs.select_related("gallery").prefetch_related("tags").all()


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Rate)
