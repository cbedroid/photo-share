from core.views import *
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestUrls(SimpleTestCase):
    def test_index_url_is_resolved(self):
        url = reverse("core:index")
        self.assertEquals(resolve(url).func.view_class, HomeListView)
