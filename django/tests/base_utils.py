import logging
import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from gallery.models import *  # noqa
from rest_framework.test import APITestCase

User = get_user_model()
logger = logging.getLogger(__name__)

PATH = os.path.dirname(os.path.abspath(__file__))
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media/")
TEST_IMAGE_DIR = os.path.join(PATH, "images/")


class PhotoShareBaseTest(TestCase):

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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.isdir(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
            logger.info("Test media Removed")

    def create_fake_image(self, name, path="test_image.jpg"):
        path = os.path.join(TEST_IMAGE_DIR, path)
        assert os.path.isfile(path)
        name = name.replace(" ", "_")
        with open(path, "rb") as image_file:
            return SimpleUploadedFile(name=name + ".jpg", content=image_file.read(), content_type="image/jpeg")


class PSAPITestCase(APITestCase, PhotoShareBaseTest):
    """Base class for PhotoShare API tests."""

    pass
