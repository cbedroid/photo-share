from django.urls import re_path

from . import views

app_name = "core"
# fmt: off
urlpatterns = [
    re_path("", views.HomeListView.as_view(), name="index"),
]
# fmt: on
