from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import *


class TestUrls(SimpleTestCase):
    def test_index_url_is_resolved(self):
        url = reverse("core:index")
        self.assertEquals(resolve(url).func.view_class, HomeListView)

    def test_album_detail_url_is_resolved(self):
        url = reverse("core:album-detail", kwargs={"slug": "some_slug"})
        self.assertEquals(resolve(url).func.view_class, AlbumDetailView)

    def test_album_create_url_is_resolved(self):
        url = reverse("core:album-create")
        self.assertEquals(resolve(url).func.view_class, AlbumCreateView)

    def test_album_update_url_is_resolved(self):
        url = reverse("core:album-update", kwargs={"slug": "some_slug"})
        self.assertEquals(resolve(url).func.view_class, AlbumUpdateView)

    def test_album_delete_url_is_resolved(self):
        url = reverse("core:album-delete", kwargs={"slug": "some_slug"})
        self.assertEquals(resolve(url).func.view_class, AlbumDeleteView)
