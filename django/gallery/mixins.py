from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import Gallery, Photo


class UserAccessPermissionMixin(PermissionRequiredMixin):
    def has_permission(self):
        """Verify whether Gallery is viewable by user"""
        user = self.request.user
        obj = self.get_object()
        # Check if object is Gallery object
        # else object must be a Photo Object
        if not isinstance(obj, Gallery):
            assert obj.__class__ == Photo
            obj = obj.gallery

        # Only allow Gallery's owner to view private gallery
        return obj.public or user == obj.user
