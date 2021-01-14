from django.urls import path, re_path
from . import views


app_name = "api"
urlpatterns = [
    # Retrieve and update
    # Gallery
    re_path(
        r"^Gallery/(?P<pk>\d+)/?$",
        views.AlbumRetrieveUpdateDestroyView.as_view(),
        name="Gallery-retrieveupdate",
    ),
    # searches and lookups
    re_path(
        r"^Gallery/", views.AlbumCreateListView.as_view(), name="Gallery-listcreate"
    ),
    re_path(
        r"^Gallery/?(?P<q>.*)/?$",
        views.AlbumCreateListView.as_view(),
        name="Gallery-listupdate",
    ),
    # Photo
    re_path(
        r"^image/(?P<pk>\d+)/?$",
        views.GalleryRetrieveUpdateDestroyView.as_view(),
        name="Photo-retrieveupdate",
    ),
    re_path(r"^image/", views.GalleryCreateListView.as_view(), name="Photo-listcreate"),
    re_path(
        r"^image/?(?P<q>.*)/?$",
        views.GalleryCreateListView.as_view(),
        name="Photo-listupdate",
    ),
    # User
    re_path(
        r"^user/(?P<pk>\d+)/?$",
        views.UserRetrieveUpdateDestroyView.as_view(),
        name="user-retrieveupdate",
    ),
    re_path(r"^user/", views.UserCreateListView.as_view(), name="user-listcreate"),
    re_path(
        r"^user/?(?P<q>.*)/?$",
        views.UserCreateListView.as_view(),
        name="user-listupdate",
    ),
]
