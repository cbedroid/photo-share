import os
from django.urls import reverse
from rest_framework.reverse import reverse as api_reverse
from django.utils.text import slugify
from django.contrib.auth.models import User,Permission,Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from core.models import *



class BaseObjectUtils(object):
    MODERATOR_GROUP = Group.objects.get(name="moderator")
    category_choices = Category.CATEGORY_LIST
    test_category = Category.objects.first()
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

    user_1 = {
        "username": "test_user_1",
        "password": "test_password",
        "email": "test_user1@test.com",
    }
    user_2 = {
        "username": "test_user_2",
        "password": "test_password",
        "email": "test_user_2@test.com",
    }

    moderator_user = {
        "username":'test_moderator',
        "email":'test_moderator@email.com',
        "password":"test_moderator_password123",
    }


    def create_test_objects(self,*args,**kwargs):
        self.create_category()
        # Test Users
        self.test_user_1 = self.create_user(**self.user_1)
        self.test_user_2 = self.create_user(**self.user_2)

        # Test Galleries
        self.test_gallery_1 = self.create_gallery(
            self.test_user_1, name="test_gallery_1"
        )
        self.test_gallery_2 = self.create_gallery(
            self.test_user_2, name="test_gallery_2"
        )

        # Test Photos
        self.test_photo_1 = self.create_photo(self.test_gallery_1, title="test_image_1")
        self.test_photo_2 = self.create_photo(self.test_gallery_2, title="test_image_2")


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
        self.gallery_api_list_url = api_reverse( "api:gallery-list")
        self.photo_api_list_url = api_reverse( "api:photo-list")
        self.user_api_list_url = api_reverse( "api:user-list")




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

    def fake_image(self, name):
        with open("core/tests/test_image.jpg", "rb") as image_file:
            return SimpleUploadedFile(
                name=name + ".jpg", content=image_file.read(), content_type="image/jpeg"
            )

    def create_photo(self, gallery, title="test_image_1"):
        return Photo.objects.create(
            title=title, image=self.fake_image(title), gallery=gallery
        )

    def create_category(self):
        # Create all categories for testing
        for index in range(len(self.category_choices)):
            Category.objects.create(
                name=index,
                label="s",
            )


      