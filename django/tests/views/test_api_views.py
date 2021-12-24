from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from gallery.models import Gallery
from model_bakery import baker
from rest_framework.test import APIClient, APITestCase
from tests.base_utils import BaseObjectUtils

User = get_user_model()


class TestGalleryViews(BaseObjectUtils, APITestCase):
    fixtures = ["test_fixtures"]

    def setUp(self):
        self.client = APIClient()
        self.client.login(**self.user_1_cred)
        self.create_test_objects()
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
        url = reverse("api:gallery-detail", kwargs={"pk": "100000000"})
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

    def test_gallery_create_method_is_successful(self):
        data = {
            "name": "some gallery",
            "public": True,
            "category": self.test_category.name,
            "title": "images",
            "image": self.create_fake_image("images.jpg"),
        }
        url = reverse("api:gallery-list")
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)

    def test_gallery_create_method_fails_if_user_not_logged_in(self):
        data = {
            "name": "some gallery",
            "public": True,
            "category": self.test_category.name,
            "title": "images",
            "image": self.create_fake_image("images.jpg"),
        }
        url = reverse("api:gallery-list")

        # anonymous user
        client = APIClient()
        response = client.post(url, data=data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_gallery_create_method_fails_when_gallery_name_is_NOT_UNIQUE(self):
        data = {
            "name": self.test_gallery_1.name,
            "public": True,
            "category": self.test_category.name,
            "title": "images",
            "image": self.create_fake_image("images.jpg"),
        }
        url = reverse("api:gallery-list")
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)

        # Test response error
        self.assertEqual(str(response.data["name"][0]), "Sorry, that gallery name is already taken")

    def test_gallery_create_method_fails_if_photo_is_not_added(self):
        data = {
            "name": "testing_gallery_1",
            "category": self.test_category.name,
            "title": "images",
        }
        url = reverse("api:gallery-list")
        response = self.client.post(url, data=data, format="multipart", follow=True)
        self.assertEqual(response.status_code, 400)

        # Test response error
        self.assertEqual(str(response.data["image"][0]), "No file was submitted.")

    def test_gallery_patch_partial_update_method_is_successful(self):
        gallery = baker.make("gallery.gallery", user=self.test_user, name="some gallery", category=self.test_category)
        gallery.save()

        # updated data
        data = {
            "name": "Updated Gallery Name",
            "public": False,
        }

        url = reverse("api:gallery-detail", kwargs={"pk": gallery.pk})
        response = self.client.patch(url, data=data, format="multipart")

        # Test gallery update
        self.assertEqual(response.status_code, 200)

        # Test gallery name is now updated
        gallery.refresh_from_db()
        self.assertEqual(response.data["name"], gallery.name)
        self.assertFalse(gallery.public)

    def test_gallery_update_method_403_when_modified_by_non_authorized_user(self):
        # Test unauthorized user can not update gallery
        url = reverse("api:gallery-detail", kwargs={"pk": self.test_gallery_1.pk})
        data = {
            "name": "another_name",
            "category": self.test_category.name,
        }

        # Log in with user 2 (unauthorized user)
        client = APIClient()
        client.login(**self.user_2_cred)
        self.assertEqual(self.test_gallery_1.user, self.test_user_1)

        # Test patch method throw permission deneied 403
        response = client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_gallery_destroy_method_is_successful(self):
        gallery = baker.make("gallery.Gallery", name="some_gallery", user=self.test_user, category=self.test_category)

        url = reverse("api:gallery-detail", kwargs={"pk": gallery.pk})
        # Test gallery was deleted successfully
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 204)  # 204/MODIFIED

    def test_gallery_delete_method_403_when_modified_by_non_authorized_user(self):
        # Test unauthorized user can not update gallery
        url = reverse("api:gallery-detail", kwargs={"pk": self.test_gallery_1.pk})

        # Log in with user 2 (unauthorized user)
        client = APIClient()
        client.login(**self.user_2_cred)
        self.assertEqual(self.test_gallery_1.user, self.test_user_1)

        # Test deletion/destroy method 403
        response = client.delete(url, format="json")
        self.assertEqual(response.status_code, 403)


class TestUserViews(BaseObjectUtils, APITestCase):
    fixtures = ["test_fixtures"]

    def setUp(self):
        self.client = APIClient()
        self.client.login(**self.user_1_cred)
        self.create_test_objects()
        self.test_user = User.objects.get(pk=1)

    def test_user_basic_authentication_method(self):
        client = APIClient()
        url = reverse("api:user-list")

        data = {
            "email": "some_testemail@test.com",
            "username": "whocares",
            "password": "supersecretpassword1029",
        }

        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        get_object_or_404(User, email=data["email"])

    def test_user_creation_fails_when_email_is_taken(self):
        client = APIClient()
        url = reverse("api:user-list")

        data = {
            "email": self.test_user_1.email,
            "username": "whocares",
            "password": "supersecretpassword1029",
        }

        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data["non_field_errors"][0]), "sorry, that email or username is already taken!")

        user = User.objects.filter(username=data["username"])
        self.assertFalse(user.exists())

    def test_user_creation_fails_when_username_is_taken(self):
        client = APIClient()
        url = reverse("api:user-list")

        data = {
            "email": "some_rando_email@test.com",
            "username": self.test_user_1.username,
            "password": "supersecretpassword1029",
        }

        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        user = User.objects.filter(email=data["email"])
        self.assertFalse(user.exists())
