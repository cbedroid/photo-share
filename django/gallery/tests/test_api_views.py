from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from gallery.enums import GalleryCategory
from gallery.models import Gallery, Photo
from templates.gallery.factories import GalleryFactory, PhotoFactory, TagFactory
from tests.base_utils import PSAPITestCase
from users.factories import PermissionFactory, UserFactory

User = get_user_model()


class TestGalleryListAPIViews(PSAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_user = UserFactory()
        cls.gallery = GalleryFactory(user=cls.current_user)
        cls.gallery_api_list_url = reverse("api:gallery-list")

    def setUp(self):
        self.client.force_authenticate(user=self.current_user)

    def test_list_gallery_renders_properly(self):
        response = self.client.get(self.gallery_api_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_filter_by_gallery_exist(self):
        response = self.client.get(
            self.gallery_api_list_url,
            {"gallery": self.gallery.id},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(data[0]["id"], self.gallery.id)
        self.assertTrue(Gallery.objects.filter(id=self.gallery.id).exists())

    def test_super_user_filter_by_private_gallery_exist(self):

        super_user = UserFactory(is_superuser=True)
        gallery_owner = UserFactory()
        private_gallery = GalleryFactory(user=gallery_owner, public=False)

        self.client.force_authenticate(user=super_user)
        response = self.client.get(
            self.gallery_api_list_url,
            {"gallery": private_gallery.id},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(data[0]["id"], private_gallery.id)

    def test_filter_by_gallery_does_not_list_private_galleries(self):
        # Test Gallery API ListView does not list private galleries
        # that are not own by the current user
        gallery_owner = UserFactory()
        private_gallery = GalleryFactory(user=gallery_owner, public=False)
        response = self.client.get(
            self.gallery_api_list_url,
            {"gallery": self.gallery.id},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        gallery_ids = [result["id"] for result in data]
        self.assertNotIn(private_gallery.id, gallery_ids)

    def test_filter_gallery_does_not_exist(self):
        response = self.client.get(
            self.gallery_api_list_url,
            {"gallery": 1000},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(len(data), 0)
        self.assertTrue(Gallery.objects.filter(id=self.gallery.id).exists())

    def test_filter_by_category_exist(self):
        response = self.client.get(
            self.gallery_api_list_url,
            {"category": self.gallery.category.name},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(data[0]["id"], self.gallery.id)
        self.assertTrue(Gallery.objects.filter(id=self.gallery.id).exists())

    def test_filter_by_category_does_not_exist(self):
        response = self.client.get(
            self.gallery_api_list_url,
            {"category": GalleryCategory.FASHION},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(len(data), 0)
        self.assertTrue(Gallery.objects.filter(id=self.gallery.id).exists())

    def test_filter_by_category_bad_request(self):
        expected_category = "UNKNOWN"
        response = self.client.get(
            self.gallery_api_list_url,
            {"category": expected_category},
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_gallery_not_allowed(self):
        response = self.client.post(
            self.gallery_api_list_url,
            data={"name": "new gallery"},
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


class TestGalleryDetailAPIViews(PSAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_user = UserFactory()
        cls.gallery = GalleryFactory(user=cls.current_user)
        cls.gallery_api_detail_url = "api:gallery-detail"

    def test_retrieve_gallery_success(self):
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": self.gallery.pk},
        )
        self.client.force_authenticate(user=self.current_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data
        self.assertEqual(data["id"], self.gallery.id)

    def test_retrieve_gallery_not_found(self):
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": self.gallery.pk + 1000},
        )

        self.client.force_authenticate(user=self.current_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_gallery_owner_can_retrieve_private_gallery(self):
        # Test owner can access his/her private gallery
        gallery = GalleryFactory(user=self.current_user, public=False)
        self.client.force_authenticate(user=self.current_user)
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": gallery.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_owner_can_not_retrieve_private_gallery(self):
        # Test user does not have permission to
        # view other users private galleries.
        gallery_owner = UserFactory()
        gallery = GalleryFactory(user=gallery_owner, public=False)

        self.client.force_authenticate(user=self.current_user)
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": gallery.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_patch_gallery_not_allowed(self):
        self.client.force_authenticate(user=self.current_user)
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": self.gallery.pk},
        )
        response = self.client.patch(
            url,
            data={"name": "new gallery"},
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_owner_can_delete_gallery_successfully(self):
        gallery_owner = UserFactory()
        gallery = GalleryFactory(user=gallery_owner, public=False)

        self.client.force_authenticate(user=gallery_owner)
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": gallery.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_staff_can_delete_gallery_successfully(self):
        gallery_owner = UserFactory()
        gallery = GalleryFactory(user=gallery_owner, public=False)
        staff_user = UserFactory(
            is_staff=True,
            user_permissions=(PermissionFactory(codename="view_gallery"),),
        )
        self.client.force_authenticate(user=staff_user)
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": gallery.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_non_owner_can_not_delete_gallery(self):
        gallery_owner = UserFactory()
        gallery = GalleryFactory(user=gallery_owner, public=False)

        nosey_user = UserFactory(username="nosey_user")
        self.client.force_authenticate(user=nosey_user)
        url = reverse(
            self.gallery_api_detail_url,
            kwargs={"pk": gallery.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestPhotoListAPIViews(PSAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_user = UserFactory()
        cls.gallery = GalleryFactory(user=cls.current_user)
        cls.photo = PhotoFactory(is_cover=False, gallery=cls.gallery)
        cls.photo_api_list_url = reverse("api:photo-list")

    def setUp(self):
        self.client.force_authenticate(user=self.current_user)

    def test_list_photo_renders_properly(self):
        response = self.client.get(self.photo_api_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_filter_by_photo_title_exist(self):
        response = self.client.get(
            self.photo_api_list_url,
            {"title": self.photo.title},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(data[0]["id"], self.photo.id)

    def test_filter_by_photo_title_does_not_exist(self):
        response = self.client.get(
            self.photo_api_list_url,
            {"title": "Unknown Photo Title"},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(len(data), 0)

    def test_filter_by_tag_name_exist(self):
        tag = TagFactory()
        photo = PhotoFactory(tags=(tag,))
        response = self.client.get(
            self.photo_api_list_url,
            {"tag_name": tag.name},
        )
        data = response.data["results"]
        self.assertEqual(data[0]["id"], photo.id)

    def test_filter_by_is_cover_exist(self):
        # By default, the first photo created for a gallery
        # is set to the cover. See gallery.signals
        response = self.client.get(
            self.photo_api_list_url,
            {"is_cover": True},
        )
        data = response.data["results"]
        self.assertEqual(data[0]["id"], self.photo.id)

    def test_filter_by_gallery_name_exist(self):
        response = self.client.get(self.photo_api_list_url, {"gallery_name": self.gallery.name})
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(data[0]["id"], self.photo.id)

    def test_filter_gallery_name_does_not_exist(self):
        response = self.client.get(
            self.photo_api_list_url,
            {"gallery_name": "Unknown"},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(len(data), 0)

    def test_filter_by_gallery_category_exist(self):
        response = self.client.get(
            self.photo_api_list_url,
            {"category": self.gallery.category.name},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.data["results"]
        self.assertEqual(data[0]["id"], self.photo.id)

    def test_filter_by_category_does_not_exist(self):
        response = self.client.get(
            self.photo_api_list_url,
            {"category": GalleryCategory.FASHION},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data["results"]
        self.assertEqual(len(data), 0)

    def test_filter_by_category_bad_request(self):
        expected_category = "UNKNOWN"
        response = self.client.get(
            self.photo_api_list_url,
            {"category": expected_category},
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_photo_not_allowed(self):
        response = self.client.post(
            self.photo_api_list_url,
            data={"name": "new photo"},
        )
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


class TestPhotoDetailAPIViews(PSAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_user = UserFactory()
        cls.gallery = GalleryFactory(user=cls.current_user)
        cls.photo = PhotoFactory(gallery=cls.gallery)
        cls.photo_api_detail_url = "api:photo-detail"

    def test_retrieve_photo_success(self):
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": self.photo.pk},
        )
        self.client.force_authenticate(user=self.current_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.data
        self.assertEqual(data["id"], self.photo.id)

    def test_retrieve_photo_not_found(self):
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": self.photo.pk + 1000},
        )
        self.client.force_authenticate(user=self.current_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_gallery_owner_can_retrieve_photo_from_private_gallery(self):
        # Test owner can access his/her photos in private gallery
        gallery = GalleryFactory(user=self.current_user, public=False)
        photo = PhotoFactory(gallery=gallery)

        self.client.force_authenticate(user=self.current_user)
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": photo.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_owner_can_not_retrieve_private_photos(self):
        # Test user does not have permission to view
        # other users private photos
        gallery_owner = UserFactory()
        gallery = GalleryFactory(user=gallery_owner, public=False)
        photo = PhotoFactory(gallery=gallery)

        self.client.force_authenticate(user=self.current_user)
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": photo.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_patch_photo_not_allowed(self):
        self.client.force_authenticate(user=self.current_user)
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": self.photo.pk},
        )
        response = self.client.patch(url, data={"name": "new gallery"})
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_owner_can_delete_photo_successfully(self):
        gallery_owner = UserFactory()
        photo = PhotoFactory(gallery__user=gallery_owner)

        self.client.force_authenticate(user=gallery_owner)
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": photo.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_deleting_photo_delete_gallery(self):
        # Test delete the last photo on a gallery also deletes the gallery
        gallery_owner = UserFactory()
        gallery = GalleryFactory(user=gallery_owner, public=False)
        photo = PhotoFactory(gallery=gallery)

        self.client.force_authenticate(user=gallery_owner)
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": photo.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(Gallery.objects.filter(pk=gallery.pk).exists())
        self.assertFalse(Photo.objects.filter(pk=photo.pk).exists())

    def test_staff_can_delete_photo_successfully(self):
        gallery_owner = UserFactory()
        photo = PhotoFactory(gallery__user=gallery_owner)
        staff_user = UserFactory(
            is_staff=True,
            user_permissions=(PermissionFactory(codename="view_photo"),),
        )
        self.client.force_authenticate(user=staff_user)
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": photo.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_non_owner_can_not_delete_photo(self):
        gallery_owner = UserFactory()
        photo = PhotoFactory(gallery__user=gallery_owner)

        nosey_user = UserFactory(username="nosey_user")
        self.client.force_authenticate(user=nosey_user)
        url = reverse(
            self.photo_api_detail_url,
            kwargs={"pk": photo.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
