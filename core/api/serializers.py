import re
import json
from rest_framework import serializers
from django.forms.models import model_to_dict
from core.models import Gallery, Photo
from django.contrib.auth.models import User


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = "__all__"

    def to_representation(self, instance):
        # Converting the timezone DateFields
        # into a string representation date format
        representation = super().to_representation(instance)
        date_format = "%m-%d-%Y"
        representation["updated"] = instance.updated.strftime(date_format)
        representation["created"] = instance.created.strftime(date_format)
        return representation

    def validate_name(self, value):
        # validate Albums name are not the same
        qs = Gallery.objects.filter(name__iexact=value)
        if self.instance:
            # if the object is actually the object itself
            # then exclude itself
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, that Gallery name has already been used "
            )
        return value


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"

    def to_representation(self, instance):
        # Converting the timezone DateFields
        # into a string representation date format
        representation = super().to_representation(instance)
        date_format = "%m-%d-%Y"
        representation["updated"] = instance.updated.strftime(date_format)
        representation["created"] = instance.created.strftime(date_format)
        return representation

    def validate_title(self, value):
        # validate Photo titles are not the same

        value = value or ""
        value = re.sub(r"\s{1,}", " ", value).strip()
        qs = Gallery.objects.filter(title__iexact=value)
        if self.instance:
            # if the object is actually the object itself
            # then exclude itself
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, that image title is already taken. Try again"
            )
        return value


class AlbumListingField(serializers.RelatedField):
    queryset = Gallery.objects.all()

    def to_representation(self, value):
        Gallery = model_to_dict(value)
        images = Gallery["images"]
        if images:
            Gallery["images"] = [x.pk for x in images]

        return "{id: %d , Gallery: %s}" % (Gallery["id"], Gallery["name"])


class UserSerializer(serializers.ModelSerializer):
    albums = AlbumListingField(source="album_set", many=True)

    class Meta:
        model = User
        fields = ["pk", "username", "albums"]

    def validate_username(self, value):
        # validate Gallery names are not the same
        value = value or ""
        value = re.sub(r"\s{1,}", " ", value).strip()
        qs = Gallery.objects.filter(username__iexact=value)
        if self.instance:
            # if the object is actually the object itself
            # then exclude itself
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Sorry, that user does not exist")
        return value
