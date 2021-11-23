from django.db import models
from django.db.models import Q


class GalleryManager(models.Manager):
    def query_search(self, query=None, qs=None):
        qs = qs or self.get_queryset()
        if query is not None:
            gallery_lookups = (
                Q(name__icontains=query) | Q(user__username__icontains=query) | Q(category__slug__icontains=query)
            )
            qs = qs.filter(gallery_lookups).distinct()
        return qs
