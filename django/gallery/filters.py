from django_filters import rest_framework as filters
from gallery.enums import GalleryCategory
from gallery.models import Gallery, Photo
from users.models import User


class GalleryFilter(filters.FilterSet):
    gallery = filters.NumberFilter(field_name="pk", label="Gallery")
    category = filters.ChoiceFilter(
        field_name="category__name",
        choices=GalleryCategory.choices,
    )

    class Meta:
        model = Gallery
        fields = (
            "gallery",
            "category",
        )


class GalleryInternalFilter(GalleryFilter):
    user = filters.ModelChoiceFilter(
        field_name="user",
        queryset=User.objects.all(),
        label="Gallery owner",
    )

    class Meta:
        model = Gallery
        fields = (
            "gallery",
            "category",
            "user",
        )


class PhotoFilter(filters.FilterSet):
    title = filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Photo title",
    )
    tag_name = filters.CharFilter(
        field_name="tags__name",
        lookup_expr="icontains",
    )
    gallery_name = filters.CharFilter(
        field_name="gallery__name",
        lookup_expr="icontains",
        label="Gallery name",
    )
    category = filters.ChoiceFilter(
        field_name="gallery__category__name",
        choices=GalleryCategory.choices,
    )

    class Meta:
        model = Photo
        fields = (
            "title",
            "is_cover",
            "tag_name",
            "gallery_name",
            "category",
        )
