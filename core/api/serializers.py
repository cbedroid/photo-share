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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "email",
            "password",
        )
        extra_kwargs = { # This is crucial not to leak user password or email 
            "password": {"write_only": True, "required": True},
            "email": {"write_only": True, "required": True},
        }

    def create(self, data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        return user


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"
        read_only_fields = (
            "slug", "created",'pk',
            "updated", "gallery",
        )

    def to_representation(self, instance):
        # Converting the timezone DateFields
        # into a string representation date format
        representation = super().to_representation(instance)
        date_format = "%m-%d-%Y"
        representation["gallery"] = {"id":instance.gallery.id, "name": instance.gallery.name}
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
            # if the object is the instance, then exclude it 
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

        
   

class GallerySerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(write_only=True)
    # For Read Only - string representation of gallery photos
    photo_set = serializers.StringRelatedField(
        source="photo", many=False, read_only=True
    )

    class Meta:
        model = Gallery
        # fmt: off
        fields = (
             "id", "name", "category", 
             "public", "created", "updated",
             "user", "photo", "photo_set",
        )
        read_only_fields = ["user"]

    def get_uri(self, obj):
        request = self.context.get("request")
        return obj.get_api_url(request)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        date_format = "%m-%d-%Y"
        try:
            """ 
                On perform_create and perform_update we dont't want the 
                represention to return any related model data. we just need the
                default representation data to populate the detail view
                
                # On Create and Update
                - POST/PUT/PATCH ---> gallery-detail view
                - GET            ---> gallery-list view (This is where the related data is needed)
            """
            photo_set = instance["photo"]
            return  representation
        except:
            photo_set = list(
                dict(id=photo.id, title=photo.title) for photo in instance.photo_set.all()
            )
            representation["uri"] = self.get_uri(instance)
            representation["category"] = instance.category.get_name_display()

        representation["photos"] = photo_set
        representation["id"] = instance.pk
        representation["updated"] = instance.updated.strftime(date_format)
        representation["created"] = instance.created.strftime(date_format)
        representation["user"] = dict(
            id=instance.user.pk, username=instance.user.username
        )
        return representation

    def validate_category(self, value):
        """ Validate Category is available """
        value = re_strip(str(value))
        category = Category.choicefield_filter(value)
        if category.exists():
            return category.first()
        raise serializers.ValidationError("Sorry, that category does not exist!")

    def validate_name(self, value):
        """ Validate Albums name are not the same """

        instance = self.context.get("instance")
        qs = Gallery.objects.filter(name__iexact=value)
        if instance:
            qs = qs.exclude(name__iexact=instance.name)
        if qs.exists():
            raise serializers.ValidationError(
                "Sorry, that gallery name is already taken"
            )
        return value

    def create(self, validated_data):
        photo = validated_data.pop("photo", None)
        gallery = Gallery.objects.create(**validated_data)
        if photo:
            photo = dict(photo)
            title = photo["title"]
            image = photo["image"]
            Photo.objects.create(title=title, image=image, gallery=gallery)
        return gallery

    def partial_update(self, instance, data):
        photo = data.pop("photo", None)

        instance.name = data.pop("name", instance.name)
        instance.category = data.pop("category", instance.category)
        instance.public = data.pop("public", instance.public)
        instance.save()

        if photo:
            photo = dict(photo)
            title = photo["title"]
            image = photo["image"]
            Photo.objects.create(title=title, image=image, gallery=instance)
        return instance

