from django.test import SimpleTestCase
from django.urls import resolve, reverse
from gallery.views import *


class TestUrls(SimpleTestCase):
    def test_album_detail_url_is_resolved(self):
        url = reverse("gallery:gallery-detail", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, GalleryDetailView)

    def test_album_create_url_is_resolved(self):
        url = reverse("gallery:gallery-create")
        self.assertEquals(resolve(url).func.view_class, GalleryCreateView)

    def test_album_update_url_is_resolved(self):
        url = reverse("gallery:gallery-update", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, GalleryUpdateView)

    def test_album_delete_url_is_resolved(self):
        url = reverse("gallery:gallery-delete", kwargs={"pk": 1})
        self.assertEquals(resolve(url).func.view_class, GalleryDeleteView)
