import re
from django.contrib.auth.models import User
from .serializers import AlbumSerializer, GallerySerializer, UserSerializer
from core.models import Gallery, Photo
from rest_framework.generics import (
    mixins,
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView as RUD,
)


class UserCreateListView(mixins.CreateModelMixin, ListAPIView):
    # List View to GET and POST an User
    # api/image/ --> GET (list)
    # api/Gallery/create --> POST
    lookup_field = "pk"
    serializer_class = UserSerializer
    permission_classes = []

    def get_queryset(self, *args, **kwargs):
        qs = User.objects.all()
        query = self.request.GET.get("q")
        if query is not None:
            query = re.sub(r"\s{1,}", " ", query).strip()
            return qs.filter(username__iexact=query)
        return qs

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class UserRetrieveUpdateDestroyView(RUD):
    # Base View to GET,PUT,PATCH, and Destroy an User
    # api/Gallery/<pk>
    queryset = User.objects.all()
    lookup_field = "pk"
    serializer_class = UserSerializer
    permission_classes = []

    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class GalleryCreateListView(mixins.CreateModelMixin, ListAPIView):
    # List View to GET and POST an Image
    # api/image/ --> GET (list)
    # api/Gallery/create --> POST
    lookup_field = "pk"
    serializer_class = GallerySerializer
    permission_classes = []

    def get_queryset(self, *args, **kwargs):
        qs = Photo.objects.all()
        query = self.request.GET.get("q")
        if query is not None:
            return qs.filter(title__iexact=query)
        return qs

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class GalleryRetrieveUpdateDestroyView(RUD):
    # Base View to GET,PUT,PATCH, and Destroy Image
    # api/Gallery/<pk>
    queryset = Photo.objects.all()
    lookup_field = "pk"
    serializer_class = GallerySerializer
    permission_classes = []

    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class AlbumCreateListView(mixins.CreateModelMixin, ListAPIView):
    # List View to GET and POST an Gallery
    # api/Gallery/ --> GET (list)
    # api/Gallery/create --> POST
    lookup_field = "pk"
    serializer_class = AlbumSerializer
    permission_classes = []

    def get_queryset(self, *args, **kwargs):
        qs = Gallery.objects.all()
        query = self.request.GET.get("q")
        if query is not None:
            return qs.filter(name__iexact=query)
        return qs

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class AlbumRetrieveUpdateDestroyView(RUD):
    # Base View to GET,PUT,PATCH, and Destroy an Gallery
    # api/Gallery/<pk>
    queryset = Gallery.objects.all()
    lookup_field = "pk"
    serializer_class = AlbumSerializer
    permission_classes = []

    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}
