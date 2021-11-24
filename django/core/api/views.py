from django.contrib.auth import get_user_model
from django.db.models import Q
from gallery.models import Gallery, Photo
from rest_framework.viewsets import ModelViewSet

from .serializers import *

user = get_user_model()


class GalleryViewSet(ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer

    def get_queryset(self):
        if self.request and self.request.user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            return Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        return Gallery.objects.filter(public=True)

    def get_serializer_context(self, **kwargs):
        context = super().get_serializer_context(**kwargs)
        context["user"] = self.request.user
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(user=self.request.user)


class PhotoViewSet(ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get_queryset(self):
        if hasattr(self, "request") and self.request.user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            return Photo.objects.filter(Q(gallery__public=True) | Q(gallery__user=self.request.user))
        return Photo.objects.filter(gallery__public=True)

    def perform_destroy(self, instance):
        instance.delete()
        # Delete related gallery if it is now empty
        photo_count = instance.gallery.photos.count()
        if photo_count == 0:
            instance.gallery.delete()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
