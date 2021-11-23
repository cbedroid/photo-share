from django.apps import AppConfig


class galleryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gallery"

    def ready(self):
        import gallery.signals  # noqa
