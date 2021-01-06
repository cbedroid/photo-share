import mock
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import *


class TestView(TestCase):
    def set_user(self):
        return User.objects.create(
            username="test_user",
            email="test_user@tests.com",
            password="plain_text_password",
        )

    def set_image(self):
        fake_image = SimpleUploadedFile(
            name="test_image.jpg", content=b"", content_type="image/jpeg"
        )
        return Gallery.objects.create(title="test_image", image=fake_image)

    def set_album(self, images=[]):
        album = Album.objects.create(
            name="test_album",
            user=self.test_user,
            public=True,
        )
        if images:
            album.images.add(*images)
        return album

    def setUp(self):
        self.client = Client()
        self.test_user = self.set_user()
        self.test_image = self.set_image()
        self.test_album = self.set_album([self.test_image])

        self.list_url = reverse("core:index")  # index
        self.create_url = reverse("core:album-create")
        self.detail_url = reverse("core:album-detail", kwargs={"slug": "test_album"})
        self.update_url = reverse("core:album-update", kwargs={"slug": "test_album"})
        self.delete_url = reverse("core:album-delete", kwargs={"slug": "test_album"})

    def test_album_list_view_GET(self):
        response = self.client.get(self.list_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "core/index.html")

    def test_album_detail_view_GET(self):
        response = self.client.get(self.detail_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "core/album_detail.html")
