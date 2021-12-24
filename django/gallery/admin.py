from django.contrib import admin

from .models import Category, Gallery, Photo, Rate, Tag


class DateCreatedAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created",
        "updated",
    )


class GalleryAdmin(DateCreatedAdmin):
    list_display = ["name", "user", "public", "category"]


class PhotoAdmin(admin.ModelAdmin):
    list_display = ["title", "gallery", "is_cover"]


class CategoryAdmin(admin.ModelAdmin):
    def get_ordering(self, request):
        return ["name"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)
admin.site.register(Rate)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Photo, PhotoAdmin)
