from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from gallery.models import Gallery, Photo
from gallery.views import GalleryListView
from model_bakery import baker
from tests.base_utils import BaseObjectUtils

User = get_user_model()


class TestGalleryViews(BaseObjectUtils, TestCase):
    fixtures = ["test_fixtures"]

    def setUp(self):
        self.client = Client()
        self.client.login(**self.user_1_cred)
        self.test_user = User.objects.get(pk=1)

    def test_GalleryList_View_renders_properly(self):
        client = Client()
        url = reverse("gallery:gallery-list")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_GalleryListView_does_not_include_private_gallery(self):
        # non authenticated user
        url = reverse("gallery:gallery-list")
        factory = RequestFactory()
        request = factory.get(url)
        request.user = AnonymousUser()
        response = GalleryListView.as_view()(request)
        self.assertIsInstance(response.context_data, dict)

        # test private gallery not included in object list
        private_gallery = Gallery.objects.get(name="private_gallery")
        object_list = list(response.context_data["object_list"])
        self.assertNotIn(private_gallery, object_list)

    def test_public_GalleryDetailView_render_properly(self):
        client = Client()
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_absolute_url()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(gallery.user, self.test_user)

    def test_private_GalleryDetailView_permissions(self):
        gallery = Gallery.objects.get(pk=2)
        url = gallery.get_absolute_url()
        self.assertFalse(gallery.public)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(gallery.user, self.test_user)

        # test non authenticated user 404
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

        # test non owner access to private gallery 404 content not found
        client = Client()
        client.login(**self.user_2_cred)
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_private_GalleryUpdateView_permissions(self):
        # gallery owner test_user_1
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_update_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(gallery.user, self.test_user)

        # test non owner access to private gallery
        client = Client()
        client.login(**self.user_2_cred)
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

        # test non authenticated user is redirected to login
        client = Client()
        response = client.get(url, follow=True)
        expected_url = self.login_url + "?next=" + url
        self.assertRedirects(response, expected_url)
        self.assertEqual(response.status_code, 200)

    def test_private_GalleryUpdateView_updates_gallery(self):
        # Testing Post method
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_update_url()
        data = self.default_formset.copy()
        data["name"] = "updated_name"

        # test Gallery name updated properly
        response = self.client.post(url, data=data, follow=True)
        gallery.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(gallery.user, self.test_user)
        self.assertEqual(gallery.name, "updated_name")

        # test non owner is denied permission to updated another user gallery
        client = Client()
        client.login(**self.user_2_cred)
        response = client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 403)

        # test non authenticated user is redirected to login
        client = Client()
        response = client.post(url, data=data, follow=True)
        expected_url = self.login_url + "?next=" + url
        self.assertRedirects(response, expected_url)
        self.assertEqual(response.status_code, 200)

    def test_GalleryUpdateView_creates_photos_properly(self):
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_update_url()
        # test gallery was updated with new image new
        formset = self.default_formset.copy()
        formset["photo-0-title"] = "photoshare"
        formset["photo-0-image"] = self.create_fake_image("photoshare")

        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, 200)

        # test image was created
        image = gallery.photos.filter(title="photoshare")
        self.assertTrue(image.exists())

    def test_GalleryUpdateView_fails_without_gallery_name(self):
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_update_url()
        formset = self.default_formset.copy()

        # TEST--> test form does not update when gallery name is not provided
        formset["name"] = ""
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, 200)
        gallery.refresh_from_db()
        self.assertNotEqual(gallery.name, "")

    def test_GalleryUpdateView_fails_without_photo(self):
        # TEST--> test gallery was update fails without image
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_update_url()

        formset = self.default_formset.copy()
        formset["photo-0-title"] = "photoshare"
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFormsetError(
            response,
            formset="formset",
            form_index=0,
            field="image",
            errors="This field is required.",
        )
        # test photo was not added
        image = gallery.photos.filter(title="photoshare")
        self.assertFalse(image.exists())

    def test_GalleryUpdateView_fails_without_photo_title(self):
        # TEST--> Test gallery was update fails without title
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_update_url()
        formset = self.default_formset.copy()
        formset["photo-0-title"] = ""
        formset["photo-0-image"] = self.create_fake_image("fake_image")

        total_photos = gallery.photos.count()
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFormsetError(
            response,
            formset="formset",
            form_index=0,
            field="title",
            errors="This field is required.",
        )

        # TEST--> test gallery photo was not added
        gallery.refresh_from_db()
        self.assertEqual(gallery.photos.count(), total_photos)

    def test_GalleryUpdateView_updates_gallery_with_multiple_photos(self):
        """Test Gallery is created if one or more formset is correct"""
        # test gallery and photo was not added
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_update_url()

        # TEST--> Test gallery  fails without title
        formset = self.default_formset.copy()
        formset["name"] = "Sports Gallery"
        formset["photo-0-title"] = "Lakers Nation"
        formset["photo-0-image"] = self.create_fake_image("Showtime Lakers")
        formset["photo-1-title"] = "The Mamba"
        formset["photo-1-image"] = self.create_fake_image("Kobe_Bryant")

        response = self.client.post(url, data=formset)

        # test gallery was updated
        self.assertEquals(response.status_code, 302)
        self.assertTrue(Gallery.objects.filter(name="Sports Gallery").exists())

        # test photo exists
        self.assertTrue(Photo.objects.filter(title="Lakers Nation").exists())
        self.assertTrue(Photo.objects.filter(title="The Mamba").exists())

    def test_GalleryCreateView_renders_properly(self):
        url = self.gallery_create_url
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_GalleryCreateView_redirect_no_authenticated_user_to_login(self):
        url = self.gallery_create_url
        client = Client()
        response = client.get(url, follow=True)
        expected_url = self.login_url + "?next=" + url
        self.assertRedirects(response, expected_url)
        self.assertEquals(response.status_code, 200)

    def test_GalleryCreateView_creates_gallery(self):
        url = self.gallery_create_url

        # test gallery was updated with new image new
        formset = self.default_formset.copy()
        formset["name"] = "new gallery"
        formset["photo-0-title"] = "new image"
        formset["photo-0-image"] = self.create_fake_image("name_image")

        response = self.client.post(url, data=formset)
        self.assertEqual(response.status_code, 302)

        gallery = Gallery.objects.filter(name="new gallery")
        self.assertTrue(gallery.exists())

    def test_GalleryCreateView_fails_without_gallery_name(self):
        url = self.gallery_create_url
        formset = self.default_formset.copy()

        # TEST--> test form does not update when gallery name is not provided
        formset["name"] = ""
        total_galleries = Gallery.objects.count()
        response = self.client.post(url, data=formset)
        # test gallery was not created
        self.assertEqual(response.status_code, 200)
        self.assertEqual(total_galleries, Gallery.objects.count())

    def test_GalleryCreateView_fails_without_photo(self):
        # # TEST--> test gallery fails without image
        url = self.gallery_create_url
        formset = self.default_formset.copy()
        formset["name"] = "New Gallery"
        formset["photo-0-title"] = "new image"
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFormsetError(
            response,
            formset="formset",
            form_index=0,
            field="image",
            errors="This field is required.",
        )

    def test_GalleryCreateView_fails_without_photo_title(self):
        # test gallery and photo was not added
        url = self.gallery_create_url
        gallery = Gallery.objects.filter(name="New Gallery")
        self.assertFalse(gallery.exists())

        # TEST--> Test gallery fails without title
        total_photos = Photo.objects.count()
        formset = self.default_formset.copy()
        formset["photo-0-title"] = ""
        formset["photo-0-image"] = self.create_fake_image("fake_image")
        response = self.client.post(url, formset, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFormsetError(
            response,
            formset="formset",
            form_index=0,
            field="title",
            errors="This field is required.",
        )

        # TEST--> test gallery photo was not added
        self.assertEqual(total_photos, Photo.objects.count())

    def test_GalleryDeleteView_delete_gallery(self):
        gallery = Gallery.objects.get(pk=1)
        url = gallery.get_delete_url()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Gallery.objects.filter(name=gallery.name).exists())

    def test_PhotoDeleteView_delete_photo(self):
        gallery = Gallery.objects.get(pk=1)
        photo = gallery.photos.first()
        url = photo.get_delete_url()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Photo.objects.filter(title=photo.title).exists())

    def test_PhotoDeleteView_delete_gallery(self):
        # test gallery is also deleted if photo is the only photo in gallery
        gallery = baker.make("gallery.gallery", name="new_gallery_2", user=self.test_user)
        photo = baker.make(
            "gallery.photo", gallery=gallery, title="fake_image", image=self.create_fake_image("new_image")
        )
        self.assertEqual(gallery.photos.count(), 1)

        url = photo.get_delete_url()
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

        # test photo and gallery was deleted
        self.assertFalse(Photo.objects.filter(title=photo.title).exists())
        self.assertFalse(Gallery.objects.filter(name=gallery.name).exists())
