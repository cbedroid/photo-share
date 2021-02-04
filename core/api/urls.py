from rest_framework import routers, serializers, viewsets
from django.urls import path, re_path, include
from . import views


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"user", views.UserViewSet)
router.register(r"gallery", views.GalleryViewSet)
router.register(r"photo", views.PhotoViewSet)
app_name = "api"

urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include(router.urls)),
]


# for url in router.urls:
#     if all( x in str(url) for x in ["gallery"]):
#         print('URL:',url)

