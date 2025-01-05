from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from gallery.filters import GalleryFilter, PhotoFilter
from gallery.models import Gallery, Photo
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

from .permissions import IsOwnerOrReadOnly
from .serializers import GallerySerializer, PhotoSerializer

User = get_user_model()


class GalleryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GalleryFilter

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.has_perm("gallery.view_gallery"):
            return qs.all()
        # Query Gallery album based on its public status.
        # If the gallery belongs to the logged in, disregard "public" state
        # include his/her private galleries as well.
        return qs.filter(Q(public=True) | Q(user=user)).all()

    def get_object(self):
        # NOTE: Added get_object permission to here to alter HTTP response.
        #      Changed status 403 to 404 to hide that the gallery even exists.
        #      This can help protect against hackers by disguising that gallery is not found.
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class PhotoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PhotoFilter

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().prefetch_related("tags")
        if user.has_perm("gallery.view_photo"):
            return qs.all()
        # Query Gallery album based on its public status.
        # If the gallery belongs to the logged in, disregard "public" state
        # include his/her private galleries as well.
        return qs.filter(Q(gallery__public=True) | Q(gallery__user=user))

    def perform_destroy(self, instance):
        instance.delete()
        # Delete related gallery if it is now empty
        photo_count = instance.gallery.photos.count()
        if photo_count == 0:
            instance.gallery.delete()
