from django.shortcuts import redirect
from django.views.generic import TemplateView


class HomeListView(TemplateView):
    template_name = "core/index.html"

    def get(self, *args, **kwargs):
        # NOTE: Temporary redirect  logged in users to galleylist
        #       until index login layouts are completed
        if self.request.user.is_authenticated:
            return redirect("gallery:gallery-list")
        return super().get(*args, **kwargs)
