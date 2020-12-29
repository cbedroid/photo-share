from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import Album, Gallery


class HomeListView(ListView):
    model = Album
    template_name = "core/index.html"
    context_object_name = "albums"
    paginate_by = 25


class AlbumDetailView(DetailView):
    model = Album
    template_name = "core/album_detail.html"
    context_object_name = "album"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["album_images"] = self.object.images.all()
        return context
