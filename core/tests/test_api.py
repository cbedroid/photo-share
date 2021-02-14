import os
import shutil
import json

from model_bakery import baker
from rest_framework.reverse import reverse as api_reverse
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.contrib.auth.models import User
from core.test_utils.base_utils import BaseObjectUtils
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from core.api.views import *
from core.models import *
from core.api.serializers import *


TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media/")

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestGalleryViewSets(APITestCase,BaseObjectUtils):
    fixtures = ["test_users.json", "test_category.json", "test_galleries.json"]

    # viewset urls
    def setUp(self):
        # Base SetUp
        self.client = APIClient()
        super().create_test_objects() # BaseObjectUtils


    def tearDown(self):
        print("Ran Gallery API Test --> ",self._testMethodName)
        if os.path.isdir(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)


    def test_gallery_list_GET_method_is_successful(self):
        gallery = baker.make('core.Gallery')

        url =  api_reverse(
            "api:gallery-detail",
            kwargs={"pk": gallery.pk}
        )
        client = APIClient()
        response = client.get(url,format="json")
        self.assertEqual(response.status_code,200)

    def test_gallery_list_GET_DO_NOT_return_private_gallery(self):
       gallery = baker.make('core.Gallery',public=False,user=self.test_user_1)
       url =  api_reverse(
           "api:gallery-detail",
           kwargs={"pk":gallery.pk}
       )

       # Test non owner can not access private gallery
       client = APIClient()
       client.force_login(self.test_user_2)
       response = client.get(url,format="json")
       self.assertEqual(response.status_code,404)

       # Test owner can access his/her private gallery
       client = APIClient()
       client.force_login(self.test_user_1)
       response = client.get(url,format="json")
       self.assertEqual(response.status_code,200)


       client.force_login(self.test_user_2)
       url = api_reverse('api:gallery-list')
       response = client.get(url,format="json")
       self.assertEqual(response.status_code,200)
       result_ids = [dict(x)['id'] for x in response.data['results']]
       self.assertNotIn(gallery.pk,result_ids)


    def test_gallery_list_lookup_404_if_object_not_exist(self):
        url =  api_reverse(
            "api:gallery-detail",
            kwargs={"pk":"100000000"}
            )
        client = APIClient()
        response = client.get(url,format="json")
        self.assertEqual(response.status_code,404)


    def test_gallery_create_method_is_successful(self):
        photo = self.test_photo_1
        with open(photo.image.path,'rb') as image_data:
            data = {
                "name": "testing_gallery_1",
                "category": "1",
                "user" : str(self.test_moderator.pk),
                "public": True,
                "title": photo.title,
                "image": image_data
                }
            client = APIClient()
            client.force_authenticate(self.test_moderator)
            url = api_reverse('api:gallery-list')
            response = client.post(url,data=data,format="multipart",follow=True)
            self.assertEqual(response.status_code,201)


    def test_gallery_patch_partial_update_method_is_successful(self):
        # initial data
        gallery = baker.make('core.Gallery',user=self.test_moderator)
        photo = baker.make('core.Photo',gallery=gallery)

        # updated data
        data = {
            "name": "another_name",
            "category": "1",
            "user" : str(self.test_moderator.pk),
            "public": True,
            }

        client = self.client
        client.force_authenticate(self.test_moderator)
        url = api_reverse("api:gallery-detail", kwargs={"pk":gallery.pk})
        response = client.patch(url,data=data,format="json")

        # Test gallery update
        self.assertEqual(response.status_code,200)

        # Test gallery name is now updated
        updated_gallery = get_object_or_404(Gallery,pk=gallery.pk)
        self.assertEqual(response.data['name'], updated_gallery.name)


    def test_gallery_put_method_is_successful(self):
        gallery = baker.make('core.Gallery',user =self.test_moderator)
        photo = baker.make('core.Photo',image=self.test_photo_1.image,gallery=gallery)

        with open(photo.image.path,'rb') as image_data:
            data = model_to_dict(gallery)
            data.update({
                "name": "another_name",
                "category": "1",
                "user" : str(self.test_moderator.pk),
                "public": False,
                'title': "another_random_image",
                'image':image_data,
                })

            url = api_reverse('api:gallery-detail', kwargs = {"pk":gallery.pk})
            client = self.client
            client.force_authenticate(self.test_moderator)
            response = client.put(url,data=data,format="multipart")

            # Test gallery update
            self.assertEqual(response.status_code,200)

            # Test gallery data is now updated
            category_name = str(Category.objects.get(pk=data['category']))
            updated_gallery = get_object_or_404(Gallery,pk=gallery.pk)

            self.assertEqual(response.data['name'], data['name'])
            self.assertEqual(response.data['category'], category_name)
            self.assertEqual(response.data['public'], data['public'])

            # test numbers of photo in a Gallery
            self.assertEqual(updated_gallery.photo_set.count(),1)
            [baker.make('core.Photo',gallery=gallery) for x in range(20)]
            self.assertEqual(updated_gallery.photo_set.count(),21)


    def test_gallery_destroy_method_is_successful(self):
        gallery = baker.make('core.Gallery',user=self.test_moderator,category=self.test_category)
        photo = baker.make('core.Photo',gallery=gallery)

        client = APIClient()
        client.force_authenticate(self.test_moderator)
        url = api_reverse('api:gallery-detail', kwargs= {"pk":gallery.pk})
        # checking if gallery was indeed created,
        # before we check if it is deleted
        response = client.get(url,format="json")
        self.assertEqual(response.status_code,200)

        response = client.delete(url,format="json")
        self.assertEqual(response.status_code,204) # 204/MODIFIED

        # response = client.get(url,format="json")
        # self.assertEqual(response.status_code,404)

    def test_staff_and_moderator_have_permissions_to_perform_CRUD_on_all_gallery(self):
        # Test if staff and moderator have full permission to
        # create,update, update,and destroy a gallery

        # Test full permission to update any gallery
        staff_members = [self.test_staff,self.test_moderator]
        for member in staff_members:
            # Create initial data
            gallery = baker.make('core.Gallery',user=member)
            photo = baker.make('core.Photo',gallery=gallery)


            client = self.client
            client.force_authenticate(member)
            url = api_reverse('api:gallery-detail', kwargs= {"pk":gallery.pk})
            data = {
                "name": "another_name",
                "category": "1",
                "public": True,
                }

            # Test patch method is successful
            response = client.patch(url,data=data,format="json")
            self.assertEqual(response.status_code,200)

            # Test put method is successful
            put_data = model_to_dict(gallery)
            put_data['name'] = "different_name"
            response = client.put(url,data=put_data,format="json")
            self.assertEqual(response.status_code,200)

            # Test deletion/destroy method is successful
            response = client.delete(url,format="json")
            self.assertEqual(response.status_code,204)

    def test_gallery_create_fails_if_user_not_logged_in(self):
        photo = self.test_photo_1
        with open(photo.image.path,'rb') as image_data:
            data = {
                "name": "testing_gallery_1",
                "category": "1",
                "user" : str(self.test_moderator.pk),
                "public": True,
                "title": photo.title,
                "image": image_data
                }
            client = APIClient()
            #No force log in method here, should throw 403 error
            url = api_reverse('api:gallery-list')
            response = client.post(url,data=data,format="multipart",follow=True)
            self.assertEqual(response.status_code,403)

    def test_gallery_create_fails_when_gallery_name_is_NOT_UNIQUE(self):
        gallery = baker.make('core.Gallery',user=self.test_moderator)
        photo = baker.make('core.Photo',gallery=gallery,image=self.test_photo_1.image)

        with open(photo.image.path,'rb') as image_data:
            data = {
                "name": gallery.name, # <-- This name is already taken and should throw 404 error
                "category": "1",
                "user" : str(self.test_moderator.pk),
                "public": True,
                "title": 'random_photo_name',
                "image": image_data
                }
            client = APIClient()
            #No force log in method here, should throw 403 error
            url = api_reverse('api:gallery-list')
            response = client.post(url,data=data,format="multipart",follow=True)
            self.assertEqual(response.status_code,403)
            # Test response error
            self.assertEqual(response.data['detail'].code,'not_authenticated')


    def test_gallery_create_fails_if_photo_is_not_added(self):
        data = {
            "name": "testing_gallery_1",
            "category": "1",
            "user" : str(self.test_moderator.pk),
            "public": True,
            }
        client = APIClient()
        client.force_authenticate(self.test_moderator)
        url = api_reverse('api:gallery-list')
        response = client.post(url,data=data,format="multipart",follow=True)
        self.assertEqual(response.status_code,400)

    def test_gallery_create_fails_if_category_does_not_exist(self):
        photo = self.test_photo_1
        with open(photo.image.path,'rb') as image_data:
            data = {
                "name": "testing_gallery_1",
                "category": "1000000000000", # selection out_of_range
                "user" : str(self.test_moderator.pk),
                "public": True,
                "title": photo.title,
                "image": image_data
                }
            client = APIClient()
            client.force_authenticate(self.test_moderator)
            url = api_reverse('api:gallery-list')
            response = client.post(url,data=data,format="multipart",follow=True)
            self.assertEqual(response.status_code,400)

    def test_gallery_update_and_delete_fails_403_when_modified_by_non_authorized_owner(self):
        # Create initial data
        gallery = baker.make('core.Gallery',user=self.test_moderator)
        photo = baker.make('core.Photo',gallery=gallery)

        # test unauthorized user can not update gallery
        not_the_owner = self.create_user("hacker","Ilovehacking")
        client = self.client
        client.force_authenticate(not_the_owner)
        url = api_reverse('api:gallery-detail', kwargs= {"pk":gallery.pk})
        data = {
            "name": "another_name",
            "category": "1",
            "public": True,
            }

        # Test patch method fails
        response = client.patch(url,data=data,format="json")
        self.assertEqual(response.status_code,403)

        # Test put method fails
        put_data = model_to_dict(gallery)
        put_data['name'] = "different_name"
        response = client.put(url,data=put_data,format="json")
        self.assertEqual(response.status_code,403)

        # Test deletion/destroy method fails
        response = client.delete(url,format="json")
        self.assertEqual(response.status_code,403)


### TEST PHOTO ###
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestPhotoViewSets(APITestCase, BaseObjectUtils):
    fixtures = ["test_users.json", "test_category.json", "test_galleries.json"]

    # viewset urls
    def setUp(self):
        # Base SetUp
        self.client = APIClient()
        super().create_test_objects()  # BaseObjectUtils

    def tearDown(self):
        print("Ran Photo API Test --> ", self._testMethodName)
        if os.path.isdir(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_photo_list_GET_method_is_successful(self):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        photo = baker.make("core.Photo", gallery=gallery, image=self.test_photo_1.image)

        url = api_reverse("api:photo-list")
        client = APIClient()
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        # Test numbers of photos in gallery

        # First exclude any pre-existing photos
        existing_photo = [x.title for x in Photo.objects.all()]

        # Create multiple new photos in a gallery
        [
            baker.make(
                "core.Photo",
                gallery=gallery,
                title="dummy_photo_" + str(x + 1),
                image=self.test_photo_1.image,
            )
            for x in range(20)
        ]
        qs = PhotoViewSet().get_queryset()
        photo_queryset = qs.exclude(title__in=existing_photo)

        # assert that there were only 20 new photos created
        self.assertEqual(len(photo_queryset), 20)

    def test_photo_create_method_is_successful(self):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        with open(self.test_photo_1.image.path, "rb") as image_data:
            data = {"gallery": gallery.pk, "title": "new_photo", "image": image_data}
            client = APIClient()
            client.force_authenticate(self.test_user_1)
            url = api_reverse("api:photo-list")
            response = client.post(url, data=data, format="multipart", follow=True)
            self.assertEqual(response.status_code, 201)

    def test_photo_patch_partial_update_method_is_successful(self):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        photo = baker.make("core.Photo", gallery=gallery, image=self.test_photo_1.image)

        data = {"title": "new_photo_title"}
        client = APIClient()
        client.force_authenticate(self.test_user_1)
        url = api_reverse("api:photo-detail", kwargs={"pk":photo.pk})
        response = client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(Photo.objects.get(pk=photo.pk).title, data["title"])

    def test_photo_put_method_is_successful(self):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        photo = baker.make("core.Photo", gallery=gallery, image=self.test_photo_1.image)

        with open(self.test_photo_1.image.path, "rb") as image_data:
            data = PhotoSerializer(photo).data
            data.update(
                {
                    "gallery": gallery.pk,
                    "title": "another_title_name",
                    "image": image_data,
                }
            )
            client = APIClient()
            client.force_authenticate(self.test_user_1)
            url = api_reverse("api:photo-detail", kwargs={"pk":photo.pk})
            response = client.put(url, data=data, format="multipart", follow=True)
            self.assertEqual(response.status_code, 200)

    def test_photo_delete_method_is_successful(self):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        photo = baker.make("core.Photo", gallery=gallery, image=self.test_photo_1.image)

        data = {"title": "new_photo_title"}
        client = APIClient()
        client.force_authenticate(self.test_user_1)
        url = api_reverse("api:photo-detail", kwargs={"pk":photo.pk})
        response = client.delete(url, format="json")
        self.assertEqual(response.status_code, 204)

        # test if gallery is also deleted
        gallery_exist = Gallery.objects.filter(pk=gallery.pk).exists()
        self.assertFalse(gallery_exist)

    # def test_photo_create_method_fails_when_photo_is_not_valid(self):
    #     gallery = baker.make('core.Gallery',user=self.test_user_1)
    #     with open(self.test_photo_2.image.path,'rb') as image_data:
    #         data = {
    #             "gallery":gallery.pk,
    #             "title": "new_photo",
    #             "image": image_data
    #             }
    #         client = APIClient()
    #         client.force_authenticate(self.test_user_1)
    #         url = api_reverse('api:photo-list')
    #         response = client.post(url,data=data,format="multipart",follow=True)
    #         self.assertEqual(response.status_code,201)

    def test_photo_patch_partial_update_method_fails_when_user_is_not_the_authorized_owner_of_gallery(
        self,
    ):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        photo = baker.make("core.Photo", gallery=gallery, image=self.test_photo_1.image)

        data = {"title": "new_photo_title"}
        client = APIClient()
        client.force_authenticate(self.test_user_2)  # <-- Not the original owner
        url = api_reverse("api:photo-detail", kwargs={"pk":photo.pk})
        response = client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_photo_delete_method_fails_when_user_is_not_the_authorized_owner_of_gallery(
        self,
    ):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        photo = baker.make("core.Photo", gallery=gallery, image=self.test_photo_1.image)

        client = APIClient()
        client.force_authenticate(self.test_user_2)  # <-- Not the original owner
        url = api_reverse("api:photo-detail", kwargs={"pk":photo.pk})
        response = client.delete(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_photo_create_fails_when_gallery_does_not_exist(self):
        with open(self.test_photo_1.image.path, "rb") as image_data:
            data = {
                "gallery": "Rando Gallery",  # Fails because a gallery id not provided
                "title": "new_photo",
                "image": image_data,
            }
            client = APIClient()
            client.force_authenticate(self.test_user_1)
            url = api_reverse("api:photo-list")
            response = client.post(url, data=data, format="multipart")
            self.assertEqual(response.status_code, 400)

    def test_photo_title_uniqueness_when_one_gallery_has_multiple_photos_with_the_same_title(
        self,
    ):
        gallery = baker.make("core.Gallery", user=self.test_user_1)
        photo = baker.make("core.Photo", gallery=gallery, image=self.test_photo_1.image)

        with open(photo.image.path, "rb") as image_data:
            data = {
                "gallery": gallery.pk,
                "title": photo.title,  # <-- will fail,because title already exist in this gallery
                "image": image_data,
            }
            client = APIClient()
            client.force_authenticate(self.test_user_1)
            url = api_reverse("api:photo-list")
            response = client.post(url, data=data, format="multipart")
            self.assertEqual(response.status_code, 400)

    def test_photo_create_method_fails_when_gallery_is_not_provided(self):
        with open(self.test_photo_1.image.path, "rb") as image_data:
            data = {"gallery": "", "title": "new_photo", "image": image_data}
            client = APIClient()
            client.force_authenticate(self.test_user_1)
            url = api_reverse("api:photo-list")
            response = client.post(url, data=data, format="multipart", follow=True)
            self.assertEqual(response.status_code, 400)  # 400/BAD_REQUEST
