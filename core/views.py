import re
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import AlbumForm
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


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = "core/album_form.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_albums"] = Album.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        # Adding Album uniqueness here in validation instead of adding it to
        # the Album model.

        # This way each users can have an album with the same name as other users,
        # but each user can only have one album with pacticular name
        # Data cleaning will be handle by Model's form class

        album = Album.objects.filter(name__iexact=album_name)

        if album.exists():
            return super().form_invalid(form)

        # Bind current logged in user to album
        form.instance.user = self.request.user
        return super().form_valid(form)


# class AlbumUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Album
#     fields = ['name','public']

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)

#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == post.author:
#             return True
#         return False
