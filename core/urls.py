from django.urls import path, re_path
from . import views

app_name = "core"
urlpatterns = [
    re_path(
        r"gallery/detail/(?P<slug>.*)/$",
        views.GalleryDetailView.as_view(),
        name="gallery-detail",
    ),
    re_path(
        r"gallery/update/(?P<slug>.*)/$",
        views.GalleryUpdateView.as_view(),
        name="gallery-update",
    ),
    re_path(
        r"gallery/delete/(?P<slug>.*)/$",
        views.GalleryDeleteView.as_view(),
        name="gallery-delete",
    ),
    re_path(r"gallery/new/$", views.GalleryCreateView.as_view(), name="gallery-create"),
    path("", views.HomeListView.as_view(), name="index"),
]
