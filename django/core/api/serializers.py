from gallery.models import Category, Gallery, Photo
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "label", "slug")
        read_only_fields = fields


class GallerySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Gallery
        fields = (
            "name",
            "public",
            "slug",
            "user",
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

    def validate_title(self, value):
        # Validate Photo titles are not the same
        qs = Photo.objects.filter(title__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Sorry, that photo title is already taken. Try again")
        return value

    def create(self, validated_data):
        gallery_data = validated_data.pop("gallery")
        image_data = validated_data.pop("image")
        title_data = validated_data.pop("title")

        gallery, _ = Gallery.objects.get_or_create(name=str(gallery_data))
        photo = Photo.objects.create(title=title_data, image=image_data, gallery=gallery)
        return photo
