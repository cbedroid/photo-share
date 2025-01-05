from django.contrib.auth import get_user_model, password_validation
from django.db.models import Q
from gallery.models import Category, Gallery, Photo
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]
        extra_kwargs = {
            # NOTE: Critical - To prevent user's password and email leakage
            "password": {"write_only": True, "required": True},
            "email": {"write_only": True, "required": True},
        }

    def validate(self, data):
        # validate username and email
        user = User.objects.filter(Q(username__iexact=data["username"]) | Q(email__iexact=data["email"]))
        if user.exists():
            raise serializers.ValidationError("sorry, that email or username is already taken!")

        # Run Django default Auth validations against password
        password_validation.validate_password(data["password"], data["username"])
        return data

    def create(self, data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        # TODO: Send allauth account confirmation email to new user
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["user"] = instance.username
        galleries = getattr(instance, "gallery", None)
        representation["total_galleries"] = galleries.count() if galleries else 0
        # TODO:  properly fix this
        representation.pop("username")
        representation.pop("password")
        return representation

    def validate_username(self, value):
        """Validate User is available"""
        user = User.objects.filter(username=value)
        if user.exists():
            raise serializers.ValidationError("Sorry, that username is already taken!")
        return value


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
