import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.urls import reverse
from gallery.models import *  # noqa
from rest_framework.reverse import reverse as api_reverse

User = get_user_model()


PATH = os.path.dirname(os.path.abspath(__file__))
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media/")
TEST_IMAGE_DIR = os.path.join(PATH, "FakeImages/")


def override_setting_config():
    # Change django settings for testing
    global settings

    setattr(settings, "ACCOUNT_EMAIL_VERIFICATION", "none")
    setattr(settings, "MEDIA_ROOT", TEST_MEDIA_ROOT)
    setattr(
        settings,
        "DEBUG_TOOLBAR_CONFIG",
        {
            "INTERCEPT_REDIRECTS": False,
            "SHOW_TOOLBAR_CALLBACK": lambda enableToolBar: False,
        },
    )


class BaseObjectUtils(object):
    override_setting_config()
    fixtures = ["test_fixtures"]

    default_formset = {
        "name": "new_gallery",
        "category": ["1"],
        "public": "on",
        "photo-TOTAL_FORMS": "4",
        "photo-INITIAL_FORMS": "0",
        "photo-MIN_NUM_FORMS": "0",
        "photo-MAX_NUM_FORMS": "4",
        "photo-0-title": "",
        "photo-0-image": "",
        "photo-1-title": "",
        "photo-1-image": "",
        "photo-2-title": "",
        "photo-2-image": "",
        "photo-3-title": "",
        "photo-3-image": "",
    }

    user_1_cred = {
        "username": "test_user_1",
        "password": "test_password",
        "email": "test_user1@test.com",
    }
    user_2_cred = {
        "username": "test_user_2",
        "password": "test_password",
        "email": "test_user_2@test.com",
    }

    # Account Urls
    login_url = reverse("account_login")
    logout_url = reverse("account_logout")

    # Core Urls
    index_url = reverse("core:index")  # index

    # API URLS
    gallery_api_list_url = api_reverse("api:gallery-list")
    photo_api_list_url = api_reverse("api:photo-list")
    user_api_list_url = api_reverse("api:user-list")

    # Gallery urls
    gallery_create_url = reverse("gallery:gallery-create")
    gallery_detail_url = reverse("gallery:gallery-detail", kwargs={"pk": "1"})
    gallery_update_url = reverse("gallery:gallery-update", kwargs={"pk": "1"})
    gallery_delete_url = reverse("gallery:gallery-delete", kwargs={"pk": "1"})

    def setUp(self, *args, **kwargs):
        # Initialize test objects making them available throughout all tests.
        # Using setUp, instead of setUpClass to prevent test variable from being affect by previous/other tests
        super().setUp(*args, **kwargs)
        self.create_test_objects()

    @classmethod
    def tearDownClass(cls):
        super(BaseObjectUtils, cls).tearDownClass()
        if os.path.isdir(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
            print("Test media Removed")

    def create_test_objects(self):
        """NOTE: This function is needed, otherwise pytest will throw Database not Access Error."""

        # # Test Users
        self.test_user_1 = get_object_or_404(User, pk=1)
        self.test_user_2 = get_object_or_404(User, pk=2)

        # # Test Category
        self.test_category = Category.objects.get(pk=1)

        # # Test Galleries
        self.test_gallery_1 = get_object_or_404(Gallery, pk=1)
        self.test_gallery_2 = get_object_or_404(Gallery, pk=2)

    def create_fake_image(self, name, path="test_image.jpg"):
        path = os.path.join(TEST_IMAGE_DIR, path)
        assert os.path.isfile(path)
        name = name.replace(" ", "_")
        with open(path, "rb") as image_file:
            return SimpleUploadedFile(name=name + ".jpg", content=image_file.read(), content_type="image/jpeg")

    def create_user(self, username="test_user_1", email="test_user_1@test.com", password="test_password"):
        user, _ = User.objects.get_or_create(username=username, email=email)
        user.set_password(password)
        user.save()
        return user

    def create_gallery(self, user, name="test_gallery_1"):
        gallery, _ = Gallery.objects.get_or_create(
            name=name,
            user=user,
            public=True,
            category=self.test_category,
        )
        return gallery

    def create_photo(self, gallery, title="test_image_1", **kwargs):
        photo, _ = Photo.objects.get_or_create(
            title=title,
            image=self.create_fake_image(title, **kwargs),
            gallery=gallery,
        )
        return photo
