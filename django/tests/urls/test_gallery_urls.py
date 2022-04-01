from django.test import SimpleTestCase
from django.urls import resolve, reverse
from gallery.views import *


class TestUrls(SimpleTestCase):
    def test_gallery_list_url_is_resolved(self):
        url = reverse("gallery:gallery-list")
        self.assertEqual(resolve(url).func.view_class, GalleryListView)

    def test_gallery_detail_url_is_resolved(self):
        url = reverse("gallery:gallery-detail", kwargs={"slug": "test_gallery"})
        self.assertEqual(resolve(url).func.view_class, GalleryDetailView)

    def test_gallery_create_url_is_resolved(self):
        url = reverse("gallery:gallery-create")
        self.assertEqual(resolve(url).func.view_class, GalleryCreateView)

    def test_gallery_update_url_is_resolved(self):
        url = reverse("gallery:gallery-update", kwargs={"slug": "test_gallery"})
        self.assertEqual(resolve(url).func.view_class, GalleryUpdateView)

    def test_gallery_delete_url_is_resolved(self):
        url = reverse("gallery:gallery-delete", kwargs={"slug": "test_gallery"})
        self.assertEqual(resolve(url).func.view_class, GalleryDeleteView)

    def test_photo_detail_url_is_resolved(self):
        url = reverse("gallery:photo-detail", kwargs={"slug": "test_image"})
        self.assertEqual(resolve(url).func.view_class, PhotoDetailView)

    def test_photo_update_url_is_resolved(self):
        url = reverse("gallery:photo-update", kwargs={"slug": "test_image"})
        self.assertEqual(resolve(url).func.view_class, PhotoUpdateView)

    def test_photo_delete_url_is_resolved(self):
        url = reverse("gallery:photo-delete", kwargs={"slug": "test_image"})
        self.assertEqual(resolve(url).func.view_class, PhotoDeleteView)

    def test_photo_transfer_url_is_resolved(self):
        url = reverse("gallery:photo-transfer", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, photo_transfer)

    def test_photo_cover_update_url_is_resolved(self):
        url = reverse("gallery:photo-cover-update", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, photo_cover_update)

    def test_category_detail_url_is_resolved(self):
        url = reverse("gallery:category-detail", kwargs={"slug": "some-category"})
        self.assertEqual(resolve(url).func.view_class, CategoryDetailView)
