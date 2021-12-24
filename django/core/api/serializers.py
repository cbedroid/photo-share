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


class GallerySerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    image = serializers.ImageField(max_length=None, allow_empty_file=False, write_only=True)
    is_cover = serializers.BooleanField(default=False, initial=False)
    category = serializers.ChoiceField(choices=Category.CATEGORY_LIST)
    photos = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = "__all__"
        read_only_fields = ["user"]

    def get_uri(self, obj):
        """Get object reversed slug url"""
        request = self.context.get("request")
        # see galley models for implementation
        return obj.get_api_url(request)

    def get_fields(self, *args, **kwargs):
        # Override get_fields making related fields: `image` and `title` not required
        # on create and update methods
        fields = super(GallerySerializer, self).get_fields(*args, **kwargs)
        request = self.context.get("request")
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
        category = Category.choicefield_filter(value)
        if not category.exists():
            raise serializers.ValidationError("Sorry, that category does not exist!")
        return category.first()

    def validate_title(self, value):
        user = self.context.get("user")
        title = Photo.objects.filter(gallery__user=user, title=value)
        if title.exists():
            raise serializers.ValidationError("Sorry, that image title is already taken!")

    def validate_name(self, value):
        qs = Gallery.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(name__iexact=self.instance.name)
        if qs.exists():
            raise serializers.ValidationError("Sorry, that gallery name is already taken")
        return value

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        title = validated_data.pop("title", None)
        is_cover = validated_data.pop("is_cover", None)
        gallery = Gallery.objects.create(**validated_data)
        if image and title:
            Photo.objects.create(title=title, image=image, is_cover=is_cover, gallery=gallery)
        return gallery

    def partial_update(self, instance, validated_data):
        # Collect photo validated_data if available

        image = validated_data.pop("image", None)
        title = validated_data.pop("title", None)

        instance.name = validated_data.pop("name", instance.name)
        instance.category = validated_data.pop("category", instance.category)
        instance.public = validated_data.pop("public", instance.public)
        instance.save()

        if image and title:
            Photo.objects.create(title=title, image=image, gallery=instance)
        return instance


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        exclude = ("slug",)
        read_only_fields = ("views", "created", "pk", "updated", "downloads")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["gallery"] = {"id": instance.gallery.id, "name": instance.gallery.name}
        return representation

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
