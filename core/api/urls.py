from django.urls import path, re_path
from . import views


app_name = "api"
urlpatterns = [
    # Retrieve and update
    # Album
    re_path(
        r"^album/(?P<pk>\d+)/?$",
        views.AlbumRetrieveUpdateDestroyView.as_view(),
        name="album-retrieveupdate",
    ),
    # searches and lookups
    re_path(r"^album/", views.AlbumCreateListView.as_view(), name="album-listcreate"),
    re_path(
        r"^album/?(?P<q>.*)/?$",
        views.AlbumCreateListView.as_view(),
        name="album-listupdate",
    ),
    # Gallery
    re_path(
        r"^image/(?P<pk>\d+)/?$",
        views.GalleryRetrieveUpdateDestroyView.as_view(),
        name="gallery-retrieveupdate",
    ),
    re_path(
        r"^image/", views.GalleryCreateListView.as_view(), name="gallery-listcreate"
    ),
    re_path(
        r"^image/?(?P<q>.*)/?$",
        views.GalleryCreateListView.as_view(),
        name="gallery-listupdate",
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
