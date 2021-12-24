from django.test import SimpleTestCase
from django.urls import resolve, reverse
from gallery.views import *


class TestUrls(SimpleTestCase):
    def test_gallery_list_url_is_resolved(self):
        url = reverse("gallery:gallery-list")
        self.assertEquals(resolve(url).func.view_class, GalleryListView)

    def test_gallery_detail_url_is_resolved(self):
        url = reverse("gallery:gallery-detail", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, GalleryDetailView)

    def test_gallery_create_url_is_resolved(self):
        url = reverse("gallery:gallery-create")
        self.assertEquals(resolve(url).func.view_class, GalleryCreateView)

    def test_gallery_update_url_is_resolved(self):
        url = reverse("gallery:gallery-update", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, GalleryUpdateView)

    def test_gallery_delete_url_is_resolved(self):
        url = reverse("gallery:gallery-delete", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, GalleryDeleteView)

    def test_photo_detail_url_is_resolved(self):
        url = reverse("gallery:photo-detail", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, PhotoDetailView)

    def test_photo_update_url_is_resolved(self):
        url = reverse("gallery:photo-update", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, PhotoUpdateView)

    def test_photo_delete_url_is_resolved(self):
        url = reverse("gallery:photo-delete", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, PhotoDeleteView)

    def test_category_detail_url_is_resolved(self):
        url = reverse("gallery:category-detail", kwargs={"slug": "some-category"})
        self.assertEquals(resolve(url).func.view_class, CategoryDetailView)
