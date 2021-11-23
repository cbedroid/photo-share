from django.urls import re_path

from . import views

app_name = "gallery"
# fmt: off
urlpatterns = [
    re_path(r"^gallery/delete/(?P<pk>\d*)/$", views.GalleryDeleteView.as_view(), name="gallery-delete"),
    re_path(r"^gallery/detail/(?P<pk>\d*)/$", views.GalleryDetailView.as_view(), name="gallery-detail"),
    re_path(r"^gallery/update/(?P<pk>\d*)/$", views.GalleryUpdateView.as_view(), name="gallery-update"),
    re_path(r"^gallery/new/$", views.GalleryCreateView.as_view(), name="gallery-create"),
    re_path(r"^photo/detail/(?P<pk>\d*)/$", views.PhotoDetailView.as_view(), name="photo-detail"),
    re_path(r"^photo/delete/(?P<pk>\d+)/$", views.PhotoDeleteView.as_view(), name="photo-delete"),
    re_path(r"^category/(P<slug>)/$", views.CategoryDetailView.as_view(), name="category-detail"),
]
# fmt: on
