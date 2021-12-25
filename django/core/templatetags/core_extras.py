import re

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=False)
def tech_support_link(link_text=None, className="support-link", *args, **kwargs):
    """Helper tag to create consistent tech_support email links"""

    tech_support_email = getattr(settings, "TECH_SUPPORT_EMAIL", "photoshare.tech@gmail.com")
    if link_text is None:
        link_text = re.sub("nowornever", "NoworNever", tech_support_email.lower())

    anchor_link = f'<a class="{className}" href="mailto:{tech_support_email}" rel="noopener noreferrer" target="_blank">{link_text}</a>'
    return mark_safe(anchor_link)


def phonenumber_formatter(number=None):
    assert number is not None
    number_format = r"^(\d{1})(\d{2,3})(\d{3})(\d{4})"
    try:
        if len(str(number)) >= 11:
            number = re.sub(number_format, r"\1-\2-\3-\4", number)
        else:
            number = re.sub(number_format, r"\1\2-\3-\4", number)
    except:  # noqa: E722
        pass
    return number


@register.simple_tag(takes_context=False)
def contact_phone_number(*args, **kwargs):
    return "No contact number"
