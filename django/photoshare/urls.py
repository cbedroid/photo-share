from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path

urlpatterns = [
    re_path(r"^account/", include("users.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^api/", include("core.api.urls")),
    re_path(r"", include("core.urls")),
]


media_url = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
static_url = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += media_url
urlpatterns += static_url

# DEBUG TOOLBAR
if settings.DEBUG:
    import debug_toolbar

    urlpatterns.insert(0, re_path("__debug__/", include(debug_toolbar.urls)))
