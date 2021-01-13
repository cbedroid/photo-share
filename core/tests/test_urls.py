from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import *


class TestUrls(SimpleTestCase):
    def test_index_url_is_resolved(self):
        url = reverse("core:index")
        self.assertEquals(resolve(url).func.view_class, HomeListView)

    def test_album_detail_url_is_resolved(self):
        url = reverse("core:gallery-detail", kwargs={"slug": "some_slug"})
        self.assertEquals(resolve(url).func.view_class, GalleryDetailView)

    def test_album_create_url_is_resolved(self):
        url = reverse("core:gallery-create")
        self.assertEquals(resolve(url).func.view_class, GalleryCreateView)

    def test_album_update_url_is_resolved(self):
        url = reverse("core:gallery-update", kwargs={"slug": "some_slug"})
        self.assertEquals(resolve(url).func.view_class, GalleryUpdateView)

    def test_album_delete_url_is_resolved(self):
        url = reverse("core:gallery-delete", kwargs={"slug": "some_slug"})
        self.assertEquals(resolve(url).func.view_class, GalleryDeleteView)
