from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


def is_ajax_request(request: "HttpRequest") -> bool:
    """Determine if request is ajax or not."""
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
