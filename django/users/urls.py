from django.urls import re_path

from . import views

app_name = "user"
# fmt: off
urlpatterns = [
    re_path(r"^profile/update/(?P<slug>.*)/$", views.UserUpdateView.as_view(), name="user-update"),
    re_path(r"^account/delete/(?P<slug>.*)/$", views.UserAccountDeleteView.as_view(), name="user-delete"),
]
# fmt: on
