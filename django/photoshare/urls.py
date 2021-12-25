from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(r"^api/", include("core.api.urls")),
    re_path(r"^account/", include("allauth.urls")),
    re_path(r"^account/", include("users.urls")),
    re_path(r"^gallery/", include("gallery.urls")),
    re_path(r"", include("core.urls")),
]


# DEBUG TOOLBAR
if settings.DEBUG:
    import debug_toolbar

    urlpatterns.insert(0, re_path("__debug__/", include(debug_toolbar.urls)))
