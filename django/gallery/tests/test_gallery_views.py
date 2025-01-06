from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse
from gallery.models import Gallery, Photo
from gallery.views import GalleryListView
from templates.gallery.factories import CategoryFactory, GalleryFactory, PhotoFactory
from tests.base_utils import PhotoShareBaseTest
from users.factories import UserFactory

User = get_user_model()


class GalleryBaseTest(PhotoShareBaseTest, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.current_user = UserFactory()
        cls.gallery = GalleryFactory(user=cls.current_user)
        cls.photo = PhotoFactory(is_cover=False, gallery=cls.gallery)
        cls.gallery_list_url = reverse("gallery:gallery-list")
        cls.gallery_create_url = reverse("gallery:gallery-create")
        cls.login_url = reverse("account_login")
        cls.logout_url = reverse("account_logout")


class TestGalleryViews(GalleryBaseTest):
    def test_gallery_list_view_renders_properly(self):
        response = self.client.get(self.gallery_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_gallery_list_view_does_not_include_private_gallery(self):
        # non authenticated user
        request = self.factory.get(self.gallery_list_url)
        request.user = AnonymousUser()
        response = GalleryListView.as_view()(request)
        self.assertIsInstance(response.context_data, dict)

        # test private gallery not included in object list
        private_gallery = GalleryFactory(public=False)
        object_list = list(response.context_data["object_list"])
        self.assertNotIn(private_gallery, object_list)
        self.assertIn(self.gallery, object_list)

    def test_public_gallery_detail_view_render_properly(self):
        url = self.gallery.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.gallery.user, self.current_user)

    def test_non_gallery_owner_access_private_gallery_permissions(self):
        non_owner_user = UserFactory()
        self.client.force_login(user=non_owner_user)

        private_gallery = GalleryFactory(user=self.current_user, public=False)
        url: str = private_gallery.get_absolute_url()
        self.assertFalse(private_gallery.public)

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class GalleryCreateViewTest(GalleryBaseTest):
    def test_create_view_renders_properly(self):
        self.client.force_login(user=self.current_user)
        url = self.gallery_create_url
        response = self.client.get(url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_non_authenticated_user_are_redirected_to_login(self):
        url = self.gallery_create_url
        response = self.client.get(url, follow=True)
        expected_url = f"{self.login_url}?next={url}"
        self.assertRedirects(response, expected_url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_creates_gallery_successfully(self):
        # test gallery was updated with new image new
        new_category = CategoryFactory(name="Basketball")
        formset = self.default_formset.copy()
        formset["name"] = "Sports"
        formset["category"] = new_category.id
        formset["photo-0-title"] = "Legendary"
        formset["photo-0-image"] = self.create_fake_image("legendary")

        self.client.force_login(user=self.current_user)
        url = self.gallery_create_url
        response = self.client.post(url, data=formset)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        gallery = Gallery.objects.filter(name="Sports")
        self.assertTrue(gallery.exists())

    def test_creating_gallery_fails_without_name(self):

        # test form does not update when gallery name is not provided
        formset = self.default_formset.copy()
        new_category = CategoryFactory(name="General")
        formset["name"] = ""
        formset["category"] = new_category.id
        total_galleries = Gallery.objects.count()

        self.client.force_login(user=self.current_user)
        url = self.gallery_create_url
        response = self.client.post(url, data=formset, follow=True)
        # test new gallery was not created
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(total_galleries, Gallery.objects.count())

    def test_creating_gallery_fails_without_photo(self):
        # test gallery fails without image
        formset = self.default_formset.copy()
        new_category = CategoryFactory(name="General")
        formset["name"] = "New Gallery"
        formset["category"] = new_category.id
        formset["photo-0-title"] = "new image"

        self.client.force_login(user=self.current_user)
        url = self.gallery_create_url
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, HTTPStatus.OK)

        self.assertFormsetError(
            response,
            formset="formset",
            form_index=0,
            field="image",
            errors="This field is required.",
        )

    def test_create_gallery_fails_without_photo_title(self):
        # test gallery and photo was not added
        gallery = Gallery.objects.filter(name="New Gallery")
        self.assertFalse(gallery.exists())

        # test gallery fails without title

        total_photos = Photo.objects.count()
        formset = self.default_formset.copy()
        formset["photo-0-title"] = ""
        formset["photo-0-image"] = self.create_fake_image("fake_image")

        self.client.force_login(user=self.current_user)
        url = self.gallery_create_url
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertFormsetError(
            response,
            formset="formset",
            form_index=0,
            field="title",
            errors="This field is required.",
        )
        #  test gallery photo was not added
        self.assertEqual(total_photos, Photo.objects.count())


class GalleryUpdateViewTest(GalleryBaseTest):
    def test_owner_can_update_private_permissions(self):
        # test owner can update private gallery
        existing_gallery = GalleryFactory(name="Art", user=self.current_user)
        self.client.force_login(user=self.current_user)
        url = existing_gallery.get_update_url()

        formset = self.default_formset.copy()
        formset["name"] = "Sports"
        formset["category"] = existing_gallery.category.id

        response = self.client.post(url, data=formset, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        existing_gallery.refresh_from_db()
        self.assertEqual(existing_gallery.name, "Sports")

    def test_update_gallery_view_creates_photos_properly(self):
        existing_gallery = GalleryFactory(name="Art", user=self.current_user)
        # test gallery was updated with new image new
        formset = self.default_formset.copy()
        formset["name"] = existing_gallery.name
        formset["category"] = existing_gallery.category.id
        formset["photo-0-title"] = "photoshare"
        formset["photo-0-image"] = self.create_fake_image("photoshare")

        self.client.force_login(user=self.current_user)
        url = existing_gallery.get_update_url()
        response = self.client.post(url, data=formset, follow=True)
        self.assertEquals(response.status_code, HTTPStatus.OK)

        # test image was created
        existing_gallery.refresh_from_db()
        new_photo = existing_gallery.photos.filter(title="photoshare").first()
        self.assertIsNotNone(new_photo)

    def test_update_gallery_view_fails_without_gallery_name(self):
        existing_gallery = GalleryFactory(name="Art", user=self.current_user)
        url = existing_gallery.get_update_url()
        formset = self.default_formset.copy()

        # test form does not update when gallery name is not provided
        formset["name"] = ""
        formset["category"] = existing_gallery.category.id
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, HTTPStatus.OK)

        existing_gallery.refresh_from_db()
        self.assertNotEqual(existing_gallery.name, "")

    def test_update_gallery_view_updates_gallery_with_multiple_photos(self):
        """Test Gallery is created if one or more formset is correct"""
        # test gallery and photo was not added
        existing_gallery = GalleryFactory(name="Baseball", user=self.current_user)

        # test gallery  fails without title
        formset = self.default_formset.copy()
        formset["name"] = "Sports Gallery"
        formset["category"] = existing_gallery.category.id
        formset["photo-0-title"] = "Lakers Nation"
        formset["photo-0-image"] = self.create_fake_image("Showtime Lakers")
        formset["photo-1-title"] = "The Mamba"
        formset["photo-1-image"] = self.create_fake_image("Kobe_Bryant")

        self.client.force_login(user=self.current_user)
        url = existing_gallery.get_update_url()
        response = self.client.post(url, data=formset, follow=True)

        # test gallery was updated
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTrue(Gallery.objects.filter(name="Sports Gallery").exists())

        # test photo exists
        self.assertTrue(Photo.objects.filter(title="Lakers Nation").exists())
        self.assertTrue(Photo.objects.filter(title="The Mamba").exists())

    def test_gallery_delete_view_delete_gallery_successful(self):
        existing_gallery = GalleryFactory(user=self.current_user)

        self.client.force_login(user=self.current_user)
        url = existing_gallery.get_delete_url()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(Gallery.objects.filter(id=existing_gallery.id).exists())


class PhotoViewTest(GalleryBaseTest):
    def setUp(self):
        self.client.force_login(user=self.current_user)

    def test_photo_delete_view_delete_photo_successfully(self):
        url = self.photo.get_delete_url()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(Photo.objects.filter(id=self.photo.id).exists())

    def test_deleting_photo_deletes_gallery(self):
        # test gallery is also deleted if photo is the only photo in gallery
        url = self.photo.get_delete_url()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # test photo and gallery was deleted
        self.assertFalse(Photo.objects.filter(id=self.photo.id).exists())
        self.assertFalse(Gallery.objects.filter(id=self.gallery.id).exists())

    def test_Photo_transfer_photo_to_another_gallery_properly(self):

        new_gallery = GalleryFactory(user=self.current_user)
        existing_photo = PhotoFactory(gallery__user=self.current_user)

        url = existing_photo.get_transfer_url()
        data = {"gallery": new_gallery.id}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # test photo was transferred to new galley
        existing_photo.refresh_from_db()
        self.assertEqual(existing_photo.gallery, new_gallery)

    def test_Photo_transfer_photo_to_another_gallery_fails(self):

        gallery = GalleryFactory(user=self.current_user)
        existing_photo = PhotoFactory(gallery=gallery)
        url = existing_photo.get_transfer_url()
        data = {"gallery": 100000}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        # test photo was not transferred to new galley
        existing_photo.refresh_from_db()
        self.assertEqual(existing_photo.gallery, gallery)
