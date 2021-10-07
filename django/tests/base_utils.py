import os
import shutil

from core.models import *
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from rest_framework.reverse import reverse as api_reverse

PATH = os.path.dirname(os.path.abspath(__file__))
FIXTURE_PATH = os.path.abspath(os.path.join(PATH, "..", "fixtures/"))
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media/")
TEST_IMAGE_DIR = os.path.join(settings.BASE_DIR, "tests/mediaFixture/gallery/")


def override_setting_config():
    # Change django settings for testing
    global settings

    setattr(
        settings,
        "DEBUG_TOOLBAR_CONFIG",
        {
            "INTERCEPT_REDIRECTS": False,
            "SHOW_TOOLBAR_CALLBACK": lambda enableToolBar: False,
        },
    )


class BaseObjectUtils(object):

    fixtures = ["test_users.json", "test_category.json", "test_galleries.json", "test_photos"]
    override_setting_config()

    MODERATOR_GROUP = Group.objects.get(name="moderator")
    category_choices = Category.CATEGORY_LIST
    default_formset = {
        "name": "new_gallery",
        "category": ["1"],
        "public": "on",
        "photo-TOTAL_FORMS": "2",
        "photo-INITIAL_FORMS": "0",
        "photo-MIN_NUM_FORMS": "0",
        "photo-MAX_NUM_FORMS": "1000",
        "photo-0-title": "",
        "photo-0-image": "",
        "photo-1-title": "",
        "photo-1-image": "",
    }

    user_1_account = {
        "username": "test_user_1",
        "password": "test_password",
        "email": "test_user1@test.com",
    }
    user_2_account = {
        "username": "test_user_2",
        "password": "test_password",
        "email": "test_user_2@test.com",
    }

    moderator_account = {
        "username": "test_moderator",
        "email": "test_moderator@email.com",
        "password": "test_moderator_password123",
    }
    staff_account = {
        "username": "test_staff_user",
        "email": "test_staff_user@email.com",
        "password": "test_staff_password123",
    }

    def create_media_root(self):
        if not TEST_MEDIA_ROOT:
            shutil.copytree(TEST_IMAGE_DIR, TEST_MEDIA_ROOT)

    def create_test_objects(self, *args, **kwargs):
        self.fixtures = ["test_users", "test_category", "test_galleries", "test_photos"]

        self.create_media_root()

        self.test_category = Category.objects.get(pk=1)
        # # Test Users
        self.test_user_1 = get_object_or_404(User, pk=1)
        self.test_user_2 = get_object_or_404(User, pk=2)
        self.test_moderator = get_object_or_404(User, pk=3)
        self.test_staff = get_object_or_404(User, pk=4)

        # # Test Galleries
        self.test_gallery_1 = get_object_or_404(Gallery, pk=1)
        self.test_gallery_2 = get_object_or_404(Gallery, pk=2)
        self.test_gallery_3 = get_object_or_404(Gallery, pk=3)

        # # Test Photos
        self.test_photo_1 = self.create_photo(self.test_gallery_1, title="test_image_1")
        self.test_photo_2 = self.create_photo(
            self.test_gallery_2,
            title="test_image_2",
            path=TEST_IMAGE_DIR + "test_image_2.jpg",
        )
        self.test_photo_blank = self.create_photo(
            self.test_gallery_3,
            title="test_blank_image",
            path=TEST_IMAGE_DIR + "test_blank_image.jpg",
        )

        self.login_url = reverse("account_login")
        self.logout_url = reverse("account_logout")
        self.home_url = reverse("core:index")  # index
        self.gallery_create_url = reverse("core:gallery-create")
        self.test_gallery_detail_url = reverse(
            "core:gallery-detail",
            kwargs={
                "slug": slugify("test_gallery_1"),
                "owner": slugify(self.test_gallery_1.user.username),
            },
        )
        self.update_url = reverse(
            "core:gallery-update",
            kwargs={
                "slug": slugify("test_gallery_1"),
                "owner": slugify(self.test_gallery_1.user.username),
            },
        )
        self.delete_url = reverse(
            "core:gallery-delete",
            kwargs={
                "slug": slugify("test_gallery_1"),
                "owner": slugify(self.test_gallery_1.user.username),
            },
        )

        # API URLS
        self.gallery_api_list_url = api_reverse("api:gallery-list")
        self.photo_api_list_url = api_reverse("api:photo-list")
        self.user_api_list_url = api_reverse("api:user-list")

    def create_user(
        self,
        username="test_user_1",
        email="test_user_1@test.com",
        password="test_password",
    ):
        user, _ = User.objects.get_or_create(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        return user

    def create_gallery(self, user, name="test_gallery_1"):
        gallery, _ = Gallery.objects.get_or_create(name=name, user=user, public=True, category=self.test_category)
        return gallery

    def fake_image(self, name, path=TEST_IMAGE_DIR + "test_image_1.jpg"):
        with open(path, "rb") as image_file:
            return SimpleUploadedFile(name=name + ".jpg", content=image_file.read(), content_type="image/jpeg")

    def create_photo(self, gallery, title="test_image_1", **kwargs):
        photo, _ = Photo.objects.get_or_create(
            title=title,
            image=self.fake_image(title, **kwargs),
            gallery=gallery,
        )
        return photo

    def create_category(self):
        # Create all categories for testing
        for index in range(len(self.category_choices)):
            Category.objects.create(
                name=index,
                label="s",
            )
