from django.contrib.auth import get_user_model
from django.db.models import Q
from gallery.models import Gallery, Photo
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthOrStaff, IsOwnerOrReadOnly
from .serializers import GallerySerializer, PhotoSerializer, UserSerializer

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = (AllowAny,)
        return super(UserViewSet, self).get_permissions()


class GalleryViewSet(ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            return Gallery.objects.filter(Q(public=True) | Q(user=user))
        return Gallery.objects.filter(public=True)

    def get_object(self):
        # NOTE: Added get_object permission to here to alter HTTP response.
        #      Changed status 403 to 404 to hide that the gallery even exists.
        #      This can help protect against hackers by disgusing that gallery is not found.
        #
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
            return Photo.objects.filter(Q(gallery__public=True) | Q(gallery__user=user))
        return Photo.objects.filter(gallery__public=True)

    def perform_destroy(self, instance):
        instance.delete()
        # Delete related gallery if it is now empty
        photo_count = instance.gallery.photos.count()
        if photo_count == 0:
            instance.gallery.delete()
