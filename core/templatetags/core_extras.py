import re
import os
import random
from django import template
from django.conf import settings
from ..models import Gallery, Photo

register = template.Library()

ASIDE_URL = os.path.join(settings.BASE_DIR, "core/templates/core/snippets/aside.html")


@register.filter("replace")
def space_replace(word):
    return re.sub(" ", "_", str(word))


@register.simple_tag(takes_context=True)
def get_user_gallery(context):
    request = context["request"]
    if request.user.is_authenticated:
        user = request.user
        context["user_gallery"] = Gallery.objects.filter(user=user)
        # Interesting enough here,we are not returning any data
        # as Django documentation states. Because we are manipulating
        # the context data here. There is no need to pass additional
        # data 'user_gallery', context will handle this functionality itself.

    """
     TODO: Figure out why not returning any data here results in rendering
            a "None" value when instantiating this filter tag in the template.
            I believe the problem is cause by using the wrong filter tag here??
            I worked around this issue by returning an empty string, but this
            may not be best practice to do so. 
    """
    return ""


@register.filter("random_cover")
def random_cover(gallery):
    try:
        photo_set = gallery.photo_set.all()
        if photo_set is not None:
            return random.choices(photo_set)[0]
    except:
        pass
    return "/".join((settings.MEDIA_URL, "/defaults/default_image.jpg"))
