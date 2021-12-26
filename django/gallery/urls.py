from django.urls import re_path

from . import views

app_name = "gallery"
# fmt: off
urlpatterns = [
    re_path(r"^delete/(?P<slug>.*)/$", views.GalleryDeleteView.as_view(), name="gallery-delete"),
    re_path(r"^detail/(?P<slug>.*)/$", views.GalleryDetailView.as_view(), name="gallery-detail"),
    re_path(r"^update/(?P<slug>.*)/$", views.GalleryUpdateView.as_view(), name="gallery-update"),
    re_path(r"^collections/$", views.GalleryListView.as_view(), name="gallery-list"),
    re_path(r"^new/$", views.GalleryCreateView.as_view(), name="gallery-create"),
    re_path(r"^photo/detail/(?P<slug>.*)/$", views.PhotoDetailView.as_view(), name="photo-detail"),
    re_path(r"^photo/delete/(?P<slug>.*)/$", views.PhotoDeleteView.as_view(), name="photo-delete"),
    re_path(r"^photo/update/(?P<slug>.*)/$", views.PhotoUpdateView.as_view(), name="photo-update"),
    re_path(r"^photo/update-cover/(?P<pk>\d+)/$", views.photo_cover_update, name="photo-cover-update"),
    re_path(r"^photo/transfer/(?P<pk>\d+)/$", views.photo_transfer, name="photo-transfer"),
    re_path(r"^category/(?P<slug>.*)/$", views.CategoryDetailView.as_view(), name="category-detail"),
]
# fmt: on
