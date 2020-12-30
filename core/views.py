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

from .forms import AlbumForm,GalleryForm,GalleryFormSet
from django.forms import formset_factory
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
        context['form_title'] = "Add New Album"

        gallery_form = formset_factory(GalleryForm, extra=3)
        context['gallery_formset'] = gallery_form
        return context


    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AlbumUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Album
    fields = ['name','public']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_albums"] = Album.objects.filter(user=self.request.user)
        context['form_title'] = "Update Album"
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """ Test whether the album belongs to the current user"""
        album = self.get_object()
        if self.request.user == album.user:
            return True
        return False
