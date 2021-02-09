import re
from django.db.models import Q
from django.utils.text import slugify
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from core.models import Gallery, Photo, Category
from .serializers import *
from . import permissions
from .mixins import CRUDMixins


class GalleryViewSet(CRUDMixins, GenericViewSet): 
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [permissions.IsAuthAllowCRUDOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            qs = Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        else:
            qs = Gallery.objects.filter(public=True)
        return qs

    def get_serializer_context(self, **kwargs):
        context = super().get_serializer_context(**kwargs)
        context["user"] = self.request.user
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PhotoViewSet(CRUDMixins, GenericViewSet):  
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthAllowCRUDOrReadOnly]

    def perform_destroy(self, instance):
        instance.delete()
        # Delete related gallery if it is now empty
        photo_count = instance.gallery.photo_set.count()
        if photo_count == 0:
            instance.gallery.delete()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UserViewSet(CRUDMixins, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthAllowCRUDOrReadOnly]
