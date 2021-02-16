import os
import shutil
import pickle
from django.urls import reverse
from rest_framework.reverse import reverse as api_reverse
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import *

PATH = os.path.dirname(os.path.abspath(__file__))
FIXTURE_PATH = os.path.abspath(os.path.join(PATH, "..", "fixtures/"))
PICKLE_FILE = os.path.abspath(os.path.join(PATH, "..", "fixtures/test_pickle_file.txt"))
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media/")

# Stop Deleting here
class BaseObjectUtils(object):

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

    def pickle_save(self, obj, file_mode="ab"):
        """ Save test object for further inspection and analysis"""
        with open(PICKLE_FILE, file_mode) as pf:
            pickle.dump(obj, pf)

    def pickle_load(self, obj, file_mode="rb"):
        """ load test object for further inspection and analysis"""
        with open(PICKLE_FILE, file_mode) as pf:
            return pickle.load(obj)

    def create_test_objects(self, *args, **kwargs):
        self.fixtures = ["test_users.json", "test_category.json", "test_galleries.json"]

        self.test_category = Category.objects.get(pk=1)
        # # Test Users
        self.test_user_1 = get_object_or_404(User, pk=56)
        self.test_user_2 = get_object_or_404(User, pk=57)

        self.test_moderator = get_object_or_404(User, pk=58)

        self.test_staff = get_object_or_404(User, pk=59)

        # # Test Galleries
        self.test_gallery_1 = get_object_or_404(Gallery, pk=98)
        self.test_gallery_2 = get_object_or_404(Gallery, pk=99)
        self.test_gallery_3 = get_object_or_404(Gallery, pk=100)

        # # Test Photos
        self.test_photo_1 = self.create_photo(self.test_gallery_1, title="test_image_1")
        self.test_photo_2 = self.create_photo(
            self.test_gallery_2,
            title="test_image_2",
            path="core/fixtures/test_image_2.jpg",
        )
        self.test_photo_blank = self.create_photo(
            self.test_gallery_3,
            title="test_blank_image",
            path="core/fixtures/test_blank_image.jpg",
        )

        # self.test_photo_1 = get_object_or_404(Photo,pk=83)
        # self.test_photo_2 = get_object_or_404(Photo,pk=84)
        # self.test_photo_blank = get_object_or_404(Photo,pk=85)

        self.login_url = reverse("account_login")
        self.logout_url = reverse("account_logout")
        self.home_url = reverse("core:index")  # index
        self.create_url = reverse("core:gallery-create")
        self.detail_url = reverse(
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
        user = User.objects.create_user(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        return user

    def create_gallery(self, user, name="test_gallery_1"):
        return Gallery.objects.create(
            name=name, user=user, public=True, category=self.test_category
        )

    def fake_image(self, name, path="core/fixtures/test_image_1.jpg"):
        with open(path, "rb") as image_file:
            return SimpleUploadedFile(
                name=name + ".jpg", content=image_file.read(), content_type="image/jpeg"
            )

    def create_photo(self, gallery, title="test_image_1", **kwargs):
        return Photo.objects.create(
            title=title, image=self.fake_image(title, **kwargs), gallery=gallery
        )

    def create_category(self):
        # Create all categories for testing
        for index in range(len(self.category_choices)):
            Category.objects.create(
                name=index,
                label="s",
            )
