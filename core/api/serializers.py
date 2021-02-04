import re
import json
from rest_framework import serializers
from django.forms.models import model_to_dict
from core.models import Gallery, Photo, Category
from django.contrib.auth.models import User


def re_strip(value):
    """ Helper function to uniform and strip whitespace incoming data"""
    value = value or ""
    return re.sub(r"\s{1,}", " ", value).strip()


class GalleryListingField(serializers.RelatedField):
    def to_representation(self, instance):
        return {"id": instance.pk, "name": instance.name}


class UserSerializer(serializers.ModelSerializer):
    gallery = GalleryListingField(source="gallery_set", many=True, read_only=True)

    class Meta:
        model = User
        fields = ["pk", "username", "email", "password", "gallery"]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "email": {"write_only": True, "required": True},
        }

    def validate_username(self, value):
        # validate username doesn't exist
        # TODO: Force constraints on usernames, preventing any bad words here
        value = re_strip(value)
        qs = User.objects.filter(username__iexact=value)
        if qs.exists():
            raise serializers.ValidationError("Sorry, that user name is already taken")
        return value

    def validate_email(self, value):
        # validate email doesn't exist
        value = re_strip(value)
        qs = User.objects.filter(email__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, An account with that email already exist"
            )
        return value


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"
        read_only_fields = (
            "slug",
            "created",
            "updated",
            "gallery",
        )

    def to_representation(self, instance):
        # Converting the timezone DateFields
        # into a string representation date format
        representation = super().to_representation(instance)
        date_format = "%m-%d-%Y"
        representation["updated"] = instance.updated.strftime(date_format)
        representation["created"] = instance.created.strftime(date_format)
        return representation

    def validate_title(self, value):
        # Validate Photo titles are not the same

        # First we grab the gallery object from views
        gallery = self.context.get("gallery")
        value = re_strip(value)
        qs = Photo.objects.filter(title__iexact=value)
        if self.instance:
            # if the object is actually the object itself
            # then exclude itself
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, that photo title is already taken. Try again"
            )
        return value

    def create(self, validated_data):
        gallery = validated_data.pop("gallery")
        image_data = validated_data.pop("image")
        title_data = validated_data.pop("title")
        photo = Photo.objects.create(
            title=title_data, image=image_data, gallery=gallery
        )
        return photo


class PhotoGallerySerializer(serializers.ModelSerializer):
    # Serializer for CUD methods Gallery and Photo.
    # POST, PUT and PATCH
    # photo = PhotoSerializer(many=False)
    image = serializers.ImageField(
        required=True,
        write_only=True,
    )
    title = serializers.CharField(
        max_length=75, min_length=3, required=True, write_only=True
    )

    class Meta:
        model = Gallery
        fields = ["name", "title", "image"]

    def validate_name(self, value):
        # validate Albums name are not the same
        qs = Gallery.objects.filter(name__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, that gallery name is already taken"
            )
        return value


class GallerySerializer(serializers.ModelSerializer):
    photos = serializers.StringRelatedField(
        source="photo_set", many=False, read_only=True
    )

    extra_kwargs = {
        "name": {"required": True},
        "public": {"required": True},
    }

    class Meta:
        model = Gallery
        fields = [
            "id",
            "name",
            "public",
            "created",
            "updated",
            "user",
            "category",
            "photos",
        ]
        read_only_fields = ["user"]

    def get_uri(self, obj):
        request = self.context.get("request")
        return obj.get_api_url(request)

    def to_representation(self, instance):
        # Converting the timezone DateFields
        # into a string representation date format
        representation = super().to_representation(instance)

        date_format = "%m-%d-%Y"
        photo_set = list(
            dict(id=photo.id, title=photo.title) for photo in instance.photo_set.all()
        )
        representation["category"] = instance.category.get_name_display()
        representation["photos"] = photo_set
        representation["id"] = instance.pk
        representation["uri"] = self.get_uri(instance)
        representation["updated"] = instance.updated.strftime(date_format)
        representation["created"] = instance.created.strftime(date_format)
        representation["user"] = dict(
            id=instance.user.pk, username=instance.user.username
        )
        return representation

    def validate_category(self, value):
        # validate Category is available
        value = re_strip(str(value))
        category = Category.choicefield_filter(value)
        if category.exists():
            return category.first()
        raise serializers.ValidationError("Sorry, that category does not exist!")

    def validate_name(self, value):
        # validate Albums name are not the same
        current_gallery = self.context.get("current_gallery")
        qs = Gallery.objects.filter(name__iexact=value)
        if current_gallery:
            qs.exclude(name=current_gallery.name)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, that gallery name is already taken"
            )
        return value
