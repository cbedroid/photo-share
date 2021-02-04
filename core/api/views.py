import re
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets, status
from rest_framework.viewsets import GenericViewSet
from .serializers import *
from core.models import Gallery, Photo, Category
from rest_framework.mixins import (
    CreateModelMixin as CreateMM,
    ListModelMixin as ListMM,
    RetrieveModelMixin as RetrieveMM,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        if isinstance(obj, Gallery):
            return obj.user == request.user
        elif isinstance(obj, Photo):
            # check permission on gallery instead of photo
            # because the photo doesn't have a user,
            # but it belongs to a gallery that haver a user
            return obj.gallery.user == request.user
        elif isinstance(obj, user):
            return obj == request.user


class IsAuthAllowCRUDOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method in [
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return True
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        if isinstance(obj, Gallery):
            return obj.user == request.user
        elif isinstance(obj, Photo):
            return obj.gallery.user == request.user
        elif isinstance(obj, user):
            return obj == request.user


class CRUDMixin(CreateMM, ListMM, RetrieveMM, GenericViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def querysearch(self, queryset, field):
        # perform query search on list view GET method
        query = self.request.GET.get("q")
        if query is not None:
            query = re.sub("/", "", query)
            query_filter = {f"{field}__icontains": query}
            queryset = queryset.filter(**query_filter).distinct()
        return queryset

    def responseError(self, serializer):
        # Custom Error Response Message
        errors = serializer.errors
        errors.update({"success": False})
        return errors


class UserViewSet(CRUDMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthAllowCRUDOrReadOnly]

    def get_queryset(self):
        qs = User.objects.all()
        return self.querysearch(qs, "username")

    def get_object(self):
        # Overwrite get_object to add multiple lookups on object
        lookup = self.kwargs.get("pk", "")
        if not str(lookup).isnumeric():
            obj = get_object_or_404(User, (Q(username=sluglookup) | Q(username=lookup)))
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    @action(detail=False, methods=["post"], url_path="create")
    def create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"success": True, "status": f"User {user} was created successfully"}
            )
        else:
            return Response(
                self.responseError(serializer), status=status.HTTP_400_BAD_REQUEST
            )


class GalleryViewSet(CRUDMixin):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [IsAuthAllowCRUDOrReadOnly]
    UPDATE_METHODS = ["post", "put", "patch"]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            # This will also fix any pagination error when logic occured in template.
            qs = Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        else:
            qs = Gallery.objects.filter(public=True)
        return self.querysearch(qs, "name")

    def get_object(self):
        # Overwrite get_object to add multiple lookups on object
        lookup = self.kwargs.get("pk", "")
        if not str(lookup).isnumeric():
            obj = get_object_or_404(Gallery, Q(slug=slugify(lookup)) | Q(slug=lookup))
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    def get_serializer_context(self, **kwargs):
        context = super().get_serializer_context(**kwargs)
        context["user"] = self.request.user
        context["request"] = self.request
        return context

    def perform_update(self, serializer):
        # Add owner to saved object
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="create")
    def create_gallery(self, request, pk=None):
        serializer = PhotoGallerySerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            image = data.pop("image")
            title = data.pop("title")
            gallery = serializer.save(user=self.request.user, **data)
            Photo.objects.create(title=title, image=image, gallery=gallery)
            return Response(
                {"success": True, "status": "gallery created successfully."}
            )
        else:
            return Response(
                self.responseError(serializer), status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=UPDATE_METHODS, url_path="update/(?P<pk>.*)")
    def update_gallery(self, request, pk=None):
        obj = self.get_object()
        serializer = GallerySerializer(
            data=request.data, partial=True, context={"current_gallery": obj}
        )
        if serializer.is_valid():
            public = serializer.validated_data.get("public")
            name = serializer.validated_data.get("name")
            if not public or name:
                return Response(
                    {
                        "success": False,
                        "error": "Either name or public status must be provided.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            obj.name = name or obj.name
            obj.public = public if public is not None else obj.public
            obj.save()
            return Response(
                {"success": True, "status": "gallery name was changed successfully."}
            )
        else:
            return Response(
                self.responseError(serializer), status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=[
            "delete",
        ],
        url_path="delete/(?P<pk>.*)",
    )
    def delete_gallery(self, request, pk=None):
        # We just need to check if the object belong to the user and delete it
        obj = self.get_object()
        obj.delete()
        return Response({"success": True, "status": f"Gallery {obj} was deleted."})

    @action(detail=True, methods=["post"])
    def add_photo(self, request, pk=None):
        obj = self.get_object()
        serializer = PhotoSerializer(data=request.data, context={"object": obj})
        if serializer.is_valid():
            serializer.save(gallery=obj)
            return Response({"success": True, "status": f"Photo was added to {obj} "})
        else:
            return Response(
                self.responseError(serializer), status=status.HTTP_400_BAD_REQUEST
            )


class PhotoViewSet(CRUDMixin):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get_queryset(self):
        qs = Photo.objects.all()
        return self.querysearch(qs, "title")

    def get_object(self):
        # Overwrite get_object to add multiple lookups on object
        lookup = self.kwargs.get("pk", "")
        if not str(lookup).isnumeric():
            obj = get_object_or_404(Photo, Q(slug=slugify(lookup)) | Q(slug=lookup))
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    @action(
        detail=False,
        methods=[
            "delete",
        ],
        url_path="delete/(?P<pk>.*)",
    )
    def delete_photo(self, request, pk=None):
        # We just need to check if the object belong to the user and delete it
        obj = self.get_object()
        obj.delete()
        return Response({"success": True, "status": f"Photo {obj} was deleted."})
