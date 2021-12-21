from django.contrib.auth import get_user_model
from django.urls import reverse
from gallery.models import Gallery
from rest_framework.reverse import reverse as api_reverse
from rest_framework.test import APIClient, APITestCase
from tests.base_utils import BaseObjectUtils

User = get_user_model()


class TestGalleryViews(BaseObjectUtils, APITestCase):
    fixtures = ["test_fixtures"]

    def setUp(self):
        self.client = APIClient()
        self.client.login(**self.user_1_cred)
        self.test_user = User.objects.get(pk=1)
        self.test_user_2 = User.objects.get(pk=2)

    def test_APIListViewSet_renders_properly(self):
        url = reverse(
            "api:gallery-list",
        )

        client = APIClient()
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        # test listview does not return private gallery
        results_pks = list(x["id"] for x in dict(response.data)["results"])
        private_gallery = Gallery.objects.get(pk=2)
        self.assertNotIn(private_gallery.id, results_pks)

        # Test total numbers of Gallery available
        self.assertEqual(len(results_pks), 1)

    def test_gallery_lookup_404_if_object_not_exist(self):
        url = api_reverse("api:gallery-detail", kwargs={"pk": "100000000"})
        client = APIClient()
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, 404)

    def test_gallery_DetailView_private_gallery(self):
        gallery = Gallery.objects.get(pk=2)
        url = reverse("api:gallery-detail", kwargs={"pk": gallery.pk})

        # Test non owner can not access private gallery
        client = APIClient()
        client.force_login(self.test_user_2)
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, 404)

        # Test owner can access his/her private gallery
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # # Test total numbers of Gallery available
        # url = reverse("api:gallery-list")
        # response = self.client.get(url, format="json")
        # self.assertEqual(response.status_code, 200)
        # result_ids = [dict(x)["id"] for x in response.data["results"]]
        # self.assertNotIn(gallery.pk, result_ids)

    def test_gallery_create_method_is_successful(self):
        data = {
            "name": "new_test_gallery",
            "category": "1",
            "public": True,
            "title": "fake_image",
            "image": self.create_fake_image("fake_image"),
        }
        url = api_reverse("api:gallery-list")
        response = self.client.post(url, data=data, format="multipart")
        self.assertEqual(response.status_code, 201)
