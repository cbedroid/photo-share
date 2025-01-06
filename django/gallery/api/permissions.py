from typing import TYPE_CHECKING, Union

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from gallery.models import Gallery, Photo
from rest_framework import permissions

User = get_user_model()
if TYPE_CHECKING is True:
    from django.http import HttpRequest
    from rest_framework.views import APIView


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    CRUD_METHODS = ("POST", "PUT", "PATCH", "DELETE")

    @staticmethod
    def has_elevated_permissions(request: "HttpRequest") -> bool:
        """Check whether user has elevated permissions to access view."""
        if request.user.is_superuser:
            return True
        if request.user.is_staff:
            return True
        if request.user.groups.filter(name="moderator").exists():
            return True
        return False

    def has_permission(self, request: "HttpRequest", view: "APIView") -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in self.CRUD_METHODS:
            if self.has_elevated_permissions(request):
                return True
            # Retrieve the Gallery objects or 404 if not the owner of gallery
            gallery = get_object_or_404(Gallery, user=request.user)
            if gallery:
                return True

        return False

    def has_object_permission(
        self,
        request: "HttpRequest",
        view: "APIView",
        obj: Union[Gallery, Photo],
    ) -> bool:
        # Read permissions are allowed to any request.
        # Edit permissions are only allowed to the owner of the Gallery.
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in self.CRUD_METHODS:
            if self.has_elevated_permissions(request):
                return True
            if isinstance(obj, Gallery):
                return obj.user == request.user
            elif isinstance(obj, Photo):
                # Check permission on gallery instead of photo
                # since the photo does not have a user.
                return obj.gallery.user == request.user
            elif isinstance(obj, User):
                return obj == request.user

        return False
