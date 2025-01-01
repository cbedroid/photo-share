from django.db import models
from django.db.models import Q


class GalleryQueryset(models.QuerySet):
    def with_public_photos(self) -> models.QuerySet:
        return self.filter(public=True)

    def with_total_views(self) -> models.QuerySet:
        return self.annotate(total_views=models.Sum("photos__views"))

    def query_search(self, query_string: str) -> models.QuerySet:
        """Filter Gallery queryset based on query string"""
        gallery_lookups = (
            Q(name__icontains=query_string)
            | Q(user__username__icontains=query_string)
            | Q(category__slug__icontains=query_string)
        )
        return self.select_related("user", "category").filter(gallery_lookups).all()


class GalleryManager(models.Manager):
    def get_queryset(self) -> GalleryQueryset:

        return GalleryQueryset(self.model, using=self._db).select_related("user", "category").prefetch_related("photos")

    def with_public_photos(self) -> GalleryQueryset:
        return self.get_queryset().with_public_photos()

    def with_total_views(self) -> GalleryQueryset:
        return self.get_queryset().with_total_views()

    def query_search(self, query_string: str) -> GalleryQueryset:
        return self.get_queryset().query_search(query_string)


class PhotoQueryset(models.QuerySet):
    def with_public_photos(self) -> models.QuerySet:
        return self.filter(gallery__public=True)


class PhotoManager(models.Manager):
    def get_queryset(self) -> PhotoQueryset:

        return PhotoQueryset(self.model, using=self._db).select_related(
            "gallery",
        )

    def with_public_photos(self) -> GalleryQueryset:
        return self.get_queryset().with_public_photos()
