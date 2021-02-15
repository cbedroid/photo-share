from rest_framework import permissions, filters
from core.models import Gallery, Photo, Category


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
            # but it belongs to a gallery that have a user
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
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True
        elif isinstance(obj, Gallery):
            return obj.user == request.user
        elif isinstance(obj, Photo):
            return obj.gallery.user == request.user
        elif isinstance(obj, User):
            return obj == request.user
