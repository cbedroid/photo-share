from django.contrib import admin
from .models import Album, Gallery


class DateCreatedAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created",
        "updated",
    )


class AlbumAdmin(DateCreatedAdmin):
    filter_horizontal = ["images"]

    list_display = [
        "name",
        "user",
    ]


admin.site.register(Album, AlbumAdmin)
admin.site.register(Gallery, DateCreatedAdmin)
