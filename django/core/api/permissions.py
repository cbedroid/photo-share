from django.contrib.auth import get_user_model
from gallery.models import Gallery, Photo
from rest_framework import permissions

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # Write permissions are only allowed to the owner of the snippet.

        # If methods  in Create or Update methods
        if isinstance(obj, Gallery):
            perm = obj.user == request.user
            return perm
        elif isinstance(obj, Photo):
            # check permission on gallery instead of photo
            # because the photo doesn't have a user,
            # but it belongs to a gallery that have a user
            return obj.gallery.user == request.user
        elif isinstance(obj, User):
            return obj == request.user

        return False


class IsAuthOrStaff(permissions.BasePermission):
    CUD_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    def is_moderator(self, request):
        if request.user.is_authenticated:
            return request.user.groups.filter(name="moderator").exists()

    def has_permission(self, request, view):

        if request.user.is_authenticated and request.method in self.CUD_METHODS:
            return True
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        is_moderator = self.is_moderator(request)

        if request.method in permissions.SAFE_METHODS:
            return True

        elif request.user.is_staff or is_moderator:
            return True

        elif isinstance(obj, Gallery):
            return obj.user == request.user
        elif isinstance(obj, Photo):
            return obj.gallery.user == request.user
        elif isinstance(obj, User):
            return obj == request.user
