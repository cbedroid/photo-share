from django.contrib import admin

from .models import Category, Gallery, Photo, Rate, Tag


class DateCreatedAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created",
        "updated",
    )


class GalleryAdmin(DateCreatedAdmin):
    list_display = ["name", "user", "public", "category"]


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Rate)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Photo, DateCreatedAdmin)
