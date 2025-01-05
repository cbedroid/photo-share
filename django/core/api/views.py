from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from gallery.filters import GalleryFilter
from gallery.models import Gallery, Photo
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthOrStaff, IsOwnerOrReadOnly
from .serializers import GallerySerializer, PhotoSerializer

User = get_user_model()


class GalleryViewSet(ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthOrStaff]
    filter_backends = (DjangoFilterBackend,)
    filter_class = GalleryFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            return Gallery.objects.filter(Q(public=True) | Q(user=user))
        return Gallery.objects.with_public_photos()

    def get_object(self):
        # NOTE: Added get_object permission to here to alter HTTP response.
        #      Changed status 403 to 404 to hide that the gallery even exists.
        #      This can help protect against hackers by disguising that gallery is not found.
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

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
        user = self.request.user
        if user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            qs = Photo.objects.filter(Q(gallery__public=True) | Q(gallery__user=user))
        else:
            qs = Photo.objects.with_public_photos()
        return qs.prefetch_related("tags")

    def perform_destroy(self, instance):
        instance.delete()
        # Delete related gallery if it is now empty
        photo_count = instance.gallery.photos.count()
        if photo_count == 0:
            instance.gallery.delete()
