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
            "name",
            "public",
            "slug",
            "created_by",
            "category",
        )
        read_only_fields = fields


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        exclude = ("slug",)
        read_only_fields = (
            "views",
            "created",
            "updated",
            "downloads",
        )
