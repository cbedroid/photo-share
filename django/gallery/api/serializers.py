from gallery.models import Category, Gallery, Photo
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "label", "slug")
        read_only_fields = fields


class GallerySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    created_by = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Gallery
        fields = (
            "id",
            "name",
            "public",
            "slug",
            "created_by",
            "category",
        )
        read_only_fields = fields


class PhotoGallerySerializer(GallerySerializer):
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta(GallerySerializer.Meta):
        fields = (
            "id",
            "name",
            "category",
            "created_by",
        )
        read_only_fields = fields


class PhotoSerializer(serializers.ModelSerializer):
    gallery = PhotoGallerySerializer(read_only=True)

    class Meta:
        model = Photo
        fields = (
            "id",
            "title",
            "image",
            "is_cover",
            "views",
            "downloads",
            "slug",
            "gallery",
            "tags",
        )
        read_only_fields = fields
