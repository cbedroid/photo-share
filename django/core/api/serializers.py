import re

from django.contrib.auth import get_user_model
from gallery.models import Category, Gallery, Photo
from rest_framework import serializers

User = get_user_model()


def re_strip(value):
    """Helper function to uniform and strip whitespace incoming data"""
    value = value or ""
    return re.sub(r"\s{1,}", " ", value).strip()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]
        extra_kwargs = {
            # NOTE: Critical - prevent user's password and email leakage
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        galleries = instance.gallery
        representation["total_galleries"] = galleries.count()
        return representation

    def validate_username(self, value):
        """Validate User is available"""
        user = User.objects.filter(username=value)
        if user.exists():
            raise serializers.ValidationError("Sorry, that category does not exist!")
        return value


class GallerySerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    image = serializers.ImageField(max_length=None, allow_empty_file=False, write_only=True)
    public = serializers.BooleanField(default=True, initial=True)

    # For Read Only - string representation of gallery photos
    photos = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = "__all__"
        read_only_fields = ["user"]

    def get_uri(self, obj):
        """Get object reversed slug url"""
        request = self.context.get("request")
        return obj.get_api_url(request)

    def get_fields(self, *args, **kwargs):
        # Override get_fields making image and title not required for PATCH and PUT
        fields = super(GallerySerializer, self).get_fields(*args, **kwargs)
        request = self.context.get("request", None)
        if request and getattr(request, "method", None) in ["PUT", "PATCH"]:
            fields["image"].required = False
            fields["title"].required = False
        return fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        photos = list(dict(id=photo.id, title=photo.title) for photo in instance.photos.all())

        representation["uri"] = self.get_uri(instance)
        representation["category"] = instance.category.get_name_display()
        representation["photos"] = photos
        representation["uploader"] = dict(id=instance.user.pk, username=instance.user.username)
        return representation

    def validate_category(self, value):
        """Validate Category is available"""
        value = re_strip(str(value))
        category = Category.choicefield_filter(value)
        if category.exists():
            return category.first()
        raise serializers.ValidationError("Sorry, that category does not exist!")

    def validate_name(self, value):
        """Validate Albums name are not the same"""
        instance = self.context.get("instance")
        qs = Gallery.objects.filter(name__iexact=value)
        if instance:
            qs = qs.exclude(name__iexact=instance.name)
        if qs.exists():
            raise serializers.ValidationError("Sorry, that gallery name is already taken")
        return value

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        title = validated_data.pop("title", None)
        gallery = Gallery.objects.create(**validated_data)
        if image and title:
            Photo.objects.create(title=title, image=image, gallery=gallery)
        return gallery

    def partial_update(self, instance, data):
        # Collect photo data if available
        image = data.pop("image", None)
        title = data.pop("title", None)

        instance.name = data.pop("name", instance.name)
        instance.category = data.pop("category", instance.category)
        instance.public = data.pop("public", instance.public)
        instance.save()

        if image and title:
            Photo.objects.create(title=title, image=image, gallery=instance)
        return instance


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        exclude = ("slug",)
        read_only_fields = (
            "views",
            "created",
            "pk",
            "updated",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["gallery"] = {"id": instance.gallery.id, "name": instance.gallery.name}
        return representation

    def validate_title(self, value):
        # Validate Photo titles are not the same

        value = re_strip(value)
        qs = Photo.objects.filter(title__iexact=value)
        if self.instance:
            # if the object is the instance, then exclude it
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
