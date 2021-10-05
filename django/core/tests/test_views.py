import os
import shutil

from core.models import *
from core.test_utils.base_utils import BaseObjectUtils
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.text import slugify

# Setup a test media directory for all testing media files
# media_root = os.path.join(settings.BASE_DIR, "test_media/")
# settings.MEDIA_ROOT = media_root

TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media/")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestWebAppGalleryView(TestCase, BaseObjectUtils):
    fixtures = ["test_users.json", "test_category.json", "test_galleries.json"]

    def setUp(self):
        self.client = Client()
        super().create_test_objects()  # BaseObjectUtils

    def tearDown(self):
        print("Ran Gallery View Test --> ", self._testMethodName)
        if os.path.isdir(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_user_login(self):
        client = Client()
        logged_in_user = client.login(**self.user_1_account)
        self.assertTrue(logged_in_user)

    def test_user_logout(self):
        # Test logout redirect to home
        client = Client()
        client.login(**self.user_1_account)
        response = client.get(self.logout_url)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.home_url)

    def test_gallery_homeview_renders_properly(self):
        # Test HomeView
        response = self.client.get(self.home_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "core/index.html")

    def test_gallery_detailview_renders_properly(self):
        # Test DetailView
        response = self.client.get(self.detail_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "core/gallery_detail.html")

    def test_gallery_updateview_fails_when_access_by_non_authenticated_user(self):
        # Test response when user is NOT loogged in and  NOT rediected to login
        # NOT AUTHENTICATED TEST
        response = self.client.get(self.update_url)
        self.assertEquals(response.status_code, 302)

    def test_gallery_updateview_redirect_non_authenticated_user_to_login(self):
        # Test update view is redirect to login page when user is NOT logged in
        response = self.client.get(self.update_url, follow=True)
        expected_url = "/account/login/?next={}".format(self.update_url)
        self.assertRedirects(response, expected_url)

    def test_gallery_updateview_allows_owner_to_update_gallery(self):
        # Test gallery update view only allow updates by its creator
        # Test gallery update by creator
        client = Client()

        client.login(**self.user_1_account)
        response = client.get(self.update_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "core/gallery_form.html")

    def test_gallery_update_fails_when_user_is_not_the_owner(self):
        # Test updateview return 403 when a gallery is updated by non-creator
        # Test gallery update by non-creator
        client = Client()
        self.create_user(
            username="not_the_owner",
            email="not_the_owner@tests.com",
            password="test_password",
        )
        client.login(username="not_the_owner", password="test_password")
        response = client.get(self.update_url)
        self.assertEquals(response.status_code, 403)

    def test_gallery_can_update_name_without_imagefile(self):
        client = Client()
        client.login(**self.user_1_account)

        # test gallery name update successfully (No image )
        response = client.post(self.update_url, self.default_formset, follow=True)
        gallery = Gallery.objects.get(pk=self.test_gallery_1.pk)
        download_file = "/home/cbedroid/Downloads/test_django.html"
        with open(download_file, "wb") as testhtml:
            testhtml.write(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(gallery.name, "new_gallery")

    def test_gallery_updateview_creates_new_image_successfully(self):
        client = Client()
        client.login(**self.user_1_account)

        # create fake gallery
        test_gallery = Gallery.objects.create(
            name="Wo_bu_zhidao",
            user=self.test_user_1,
            public=True,
            category=self.test_category,
        )
        # test gallery was updated with new image new
        formset = self.default_formset.copy()
        formset["photo-0-title"] = "language"
        formset["photo-0-image"] = self.fake_image("language")

        update_url = reverse(
            "core:gallery-update",
            kwargs={
                "slug": slugify(test_gallery.slug),
                "owner": slugify(self.test_gallery_1.user.username),
            },
        )

        response = client.post(update_url, formset, follow=True)
        image = Photo.objects.filter(title="language")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(image.exists())

    def test_gallery_createview_post_fails_without_a_gallery_name(self):
        client = Client()
        client.login(**self.user_1_account)

        # test creating a gallery without a name fails
        formset = self.default_formset.copy()
        formset["name"] = ""
        response = client.post(self.create_url, formset)
        gallery = Gallery.objects.filter(name="new_created_gallery")
        self.assertEquals(response.status_code, 200)
        self.assertFalse(gallery.exists())

    def test_gallery_createview_post_fails_without_an_photo_title(self):
        client = Client()
        client.login(**self.user_1_account)

        # test create gallery fails when image file doesn't exist
        gallery_name = "test_create_gallery_1"
        photo_title = "new_image_title_1"
        formset = self.default_formset
        formset["name"] = gallery_name
        formset["photo-0-title"] = photo_title
        response = client.post(self.create_url, formset)

        image = Photo.objects.filter(title=photo_title)
        gallery = Gallery.objects.filter(name=gallery_name)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(gallery.exists())
        self.assertFalse(image.exists())

    def test_gallery_createview_post_fails_without_an_photo_file(self):
        client = Client()
        client.login(**self.user_1_account)

        # test create gallery fails when image file doesn't exist
        gallery_name = "test_create_gallery_2"
        formset = self.default_formset.copy()
        formset["name"] = gallery_name
        formset["photo-0-title"] = ""
        formset["photo-0-image"] = self.fake_image("new_image")

        response = client.post(self.create_url, formset, follow=True)
        gallery = Gallery.objects.filter(name="new_created_gallery_1")
        self.assertFalse(gallery.exists())
        self.assertEquals(response.status_code, 200)  # not created(202)

    def test_gallery_createview_post_is_successfully(self):
        client = Client()
        client.login(**self.user_1_account)

        # test create gallery fails when image file doesn't exist
        gallery_name = "test_create_gallery_3"
        photo_title = "new_image_title_3"
        formset = self.default_formset.copy()
        formset["name"] = gallery_name
        formset["photo-0-title"] = photo_title
        formset["photo-0-image"] = self.fake_image(photo_title)

        response = client.post(self.create_url, formset, follow=True)
        gallery = Gallery.objects.filter(name=gallery_name)
        image = Photo.objects.filter(title=photo_title)
        self.assertTrue(gallery.exists())
        self.assertTrue(image.exists())
        self.assertEquals(response.status_code, 200)

    # DELETE VIEW
    def test_gallery_deleteview_fails_without__being_login(self):
        client = Client()

        # test deleting a gallery without being logged.
        # view should redirect to login page
        gallery = self.test_gallery_1.name
        response = client.get(self.delete_url)
        self.assertEquals(response.status_code, 302)

        # gallery should still exist
        gallery = Gallery.objects.filter(name=gallery)
        self.assertTrue(gallery.exists())

        # Test view was redirect to login page
        expected_url = "/account/login/?next={}".format(self.delete_url)
        self.assertRedirects(response, expected_url)

    def test_gallery_deleteview_throws_403_permission_denied_when_access_by_non_owner(self):
        client = Client()
        self.create_user(
            username="not_the_owner_2",
            email="not_the_owner_2@tests.com",
            password="test_password",
        )
        client.login(username=not_the_owner.username, password="test_password")
        # Test deleting a gallery throw 403 permission denied
        gallery = self.test_gallery_1.name
        response = client.get(self.delete_url)
        self.assertEquals(response.status_code, 403)

        # Gallery object should still exist
        gallery = Gallery.objects.filter(name=gallery)
        self.assertTrue(gallery.exists())

    def test_gallery_deleteview_allows_owner_to_view_page(self):
        client = Client()
        client.login(**self.user_1_account)
        # GET Method
        # Test owner can view DeleteView
        # Test html contains delete message

        response = client.get(self.delete_url)
        # Remove this until project is finish.
        # delete_msg is subject change through out the development and may cause false failure
        delete_msg = "Are you sure you want to delete this gallery?"
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, delete_msg)

    def test_gallery_deleteview_successfully_delete_gallery(self):
        client = Client()
        client.login(**self.user_1_account)
        # POST Method
        # Test deleting a gallery is successful
        # view should redirect to login page

        gallery = self.test_gallery_1.name
        response = client.post(self.delete_url, follow=True)
        with open("/home/cbedroid/Downloads/photoshare_response.html", "wb") as wb:
            wb.write(response.content)
        self.assertEquals(response.status_code, 200)

        # gallery should now be deleted
        gallery = Gallery.objects.filter(name=gallery)
        self.assertFalse(gallery.exists())

        # Test view was redirect to home page
        self.assertRedirects(response, self.home_url)


# PHOTO TEST
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestWebAppPhotoView(TestCase, BaseObjectUtils):
    fixtures = ["test_users.json", "test_category.json", "test_galleries.json"]

    def setUp(self):
        self.client = Client()
        super().create_test_objects()  # BaseObjectUtils

    def tearDown(self):
        print("Ran Photo View Test --> ", self._testMethodName)
        if os.path.isdir(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_photo_deletion_fails_when_user_not_authenticated(self):
        client = Client()
        # POST Method
        # Test deleting a Photo fails
        # view should redirect to login page

        photo = self.create_photo(self.test_gallery_1, title="test_photo_1")
        photo_delete_url = reverse("core:photo-delete", kwargs={"pk": photo.id})
        response = client.post(photo_delete_url, follow=True)
        expected_url = "/account/login/?next={}".format(photo_delete_url)
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, expected_url)

    def test_photo_deletion_throw_404_when_photo_does_not_exist(self):
        client = Client()
        client.login(**self.user_1_account)

        # POST Method
        # Test deleting a Photo fails because photo does exists
        # view should redirect 404

        fake_photo_id = 2002002002
        photo_delete_url = reverse("core:photo-delete", kwargs={"pk": fake_photo_id})
        response = client.post(photo_delete_url, follow=True)
        self.assertEquals(response.status_code, 404)

    def test_photo_deletion_fails_when_user_is_not_the_owner(self):
        client = Client()
        client.login(**self.user_2_account)

        # POST Method
        # Test deleting a Photo fails
        # view should redirect 403

        # test_gallery_1 is owned by user_1 not user_2, so it should fail.
        photo = self.create_photo(self.test_gallery_1, title="test_photo_1")
        photo_delete_url = reverse("core:photo-delete", kwargs={"pk": photo.id})
        response = client.post(photo_delete_url, follow=True)
        self.assertEquals(response.status_code, 403)

        # check if photo still exist.
        original_photo = Photo.objects.filter(id=photo.pk)
        self.assertTrue(original_photo.exists())

    def test_photo_deletion_is_successfully(self):
        client = Client()
        client.login(**self.user_1_account)

        # POST Method
        # Test deleting a Photo is successful
        # view should to Photo's gallery detail page

        photo = self.create_photo(self.test_gallery_1, title="test_photo_1")
        photo_delete_url = reverse("core:photo-delete", kwargs={"pk": photo.id})
        response = client.post(photo_delete_url, follow=True)
        self.assertEquals(response.status_code, 200)

        # check if photo still is now deleted.
        original_photo = Photo.objects.filter(id=photo.pk)
        self.assertFalse(original_photo.exists())

        # check whether view was redirect to photo's gallery detail page
        self.assertRedirects(response, self.detail_url)

    def test_photo_deletion_also_delete_gallery_when_no_photo_exist(self):
        client = Client()
        client.login(**self.user_1_account)

        # POST Method
        # Test deleting a Photo successfully delete empty gallery
        photo = self.test_photo_1
        photo_delete_url = reverse("core:photo-delete", kwargs={"pk": photo.id})
        client.post(photo_delete_url, follow=True)
        gallery = Gallery.objects.filter(id=photo.gallery.id)
        self.assertFalse(gallery.exists())
