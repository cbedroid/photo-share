from django.urls import path, re_path
from . import views

app_name = "core"
urlpatterns = [
    path("", views.HomeListView.as_view(), name="index"),
    re_path(r"album/new/$", views.AlbumCreateView.as_view(), name="album-create"),
    re_path(
        r"album/(?P<slug>.*)/$", views.AlbumDetailView.as_view(), name="album-detail"
    ),
]
