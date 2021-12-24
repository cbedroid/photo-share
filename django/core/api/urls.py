from django.urls import re_path
from rest_framework import routers
from rest_framework.authtoken import views as token_views

from . import views

app_name = "api"
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"user", views.UserViewSet)
router.register(r"gallery", views.GalleryViewSet)
router.register(r"photo", views.PhotoViewSet)

urlpatterns = router.urls
urlpatterns += [
    re_path("^api-token-auth/$", token_views.obtain_auth_token),
]
