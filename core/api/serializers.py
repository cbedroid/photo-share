import re
from rest_framework import serializers
from core.models import Album, Gallery
from django.contrib.auth.models import User


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
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
        qs = Album.objects.filter(name__iexact=value)
        if self.instance:
            # if the object is actually the object itself
            # then exclude itself
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, that album name has already been used "
            )
        return value



class GallerySerializer(serializers.ModelSerializer):
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

    def validate_title(self, value):
        # validate gallery titles are not the same

        value = value or ""
        value = re.sub(r"\s{1,}", " ", value).strip()
        qs = Album.objects.filter(title__iexact=value)
        if self.instance:
            # if the object is actually the object itself
            # then exclude itself
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Sorry, that image title is already taken. Try again")
        return value


class AlbumListingField(serializers.RelatedField):
    queryset = Album.objects.all()

    def to_representation(self, value):
        return "id: %d %s" % (value.pk, value.name)


class UserSerializer(serializers.ModelSerializer):
    albums = AlbumListingField(source="album_set", many=True)

    class Meta:
        model = User
        fields = ["pk", "username", "albums"]

    def validate_username(self, value):
        # validate Album names are not the same
        value = value or ""
        value = re.sub(r"\s{1,}", " ", value).strip()
        qs = Album.objects.filter(username__iexact=value)
        if self.instance:
            # if the object is actually the object itself
            # then exclude itself
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Sorry, that user does not exist")
        return value
