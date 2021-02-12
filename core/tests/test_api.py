import os
import json
from core.models import *
from core.api.serializers import *
from model_bakery import baker
from django.urls import reverse, resolve
from rest_framework.reverse import reverse as api_reverse
from django.test import override_settings
from rest_framework.test  import APITestCase, APIClient
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.contrib.auth.models import User,Permission,Group
from core.test_utils.base_utils import BaseObjectUtils


class TestGalleryViewSets(APITestCase,BaseObjectUtils):

    # viewset urls
    def setUp(self):
        # Base SetUp 
        self.client = APIClient()
        super().create_test_objects() # BaseObjectUtils

        # Create user with MODERATOR's Permission
        self.moderator = self.create_user(**self.moderator_user)
        self.moderator.groups.add(self.MODERATOR_GROUP)

    def test_gallery_list_view_is_successful(self):
        gallery = baker.make('core.Gallery')

        url =  api_reverse(
            "api:gallery-detail",
            kwargs={"pk":gallery.pk}
        )
        client = APIClient()
        response = client.get(url,format="json")
        self.assertEqual(response.status_code,200)


    def test_gallery_create_view_is_successful(self):
        #photo = baker.make("core.Photo")
        photo = self.test_photo_1
        data = {
            "name": "testing_gallery_5",
            "category": "1",
            "user" : '1',
            "public": True,
            "photo":{
                "title": photo.title +"_another",
                "image": photo.image,
            }
        }

        url = api_reverse('api:gallery-list')
        client = APIClient()
        client.force_authenticate(self.moderator)
        response = client.post(url, data=data,format="json")
        print(f"""\nResponse:{response.render()}
            Data: {response.data}
            \n{dir(response)}
        """)
        self.assertEqual(response.status_code,200)

    # gallery = Gallery.objects.get(id=response.data['id'])
        # serialized_data = GallerySerializer(gallery).data
        # self.assertEqual(response.data, serialized_data)

