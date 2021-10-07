from django.urls import include, path
from rest_framework import routers

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
