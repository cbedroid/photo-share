import os
import re

from django import template
from django.conf import settings
from gallery.models import Gallery

register = template.Library()

ASIDE_URL = os.path.join(settings.BASE_DIR, "gallery/templates/gallery/snippets/aside.html")


@register.filter("replace")
def space_replace(word):
    return re.sub(" ", "_", str(word))


@register.simple_tag(takes_context=True)
def get_user_gallery(context):
    request = context["request"]
    if request.user.is_authenticated:
        user = request.user
        context["user_gallery"] = Gallery.objects.filter(user=user).order_by("-updated", "-pk")[:10]
    return ""


@register.filter("random_cover")
def random_cover(gallery_pk):
    """random select a photo from gallery"""
    try:
        qs = Gallery.objects.filter(pk=gallery_pk)
        if qs.exists():
            gallery = qs.first()
            return gallery.photos.order_by("?").first()
    except:  # noqa
        pass
