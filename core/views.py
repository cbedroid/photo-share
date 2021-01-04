import re
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import AlbumForm, GalleryForm, GalleryBaseFormSet
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


class CRUDView(LoginRequiredMixin):
    model = Album
    form_class = AlbumForm
    template_name = "core/album_form.html"
    crud_type = "create"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        GalleryFormSet = formset_factory(
            GalleryForm, formset=GalleryBaseFormSet, extra=3
        )

        if self.request.POST:
            gallery_form_set = GalleryFormSet(
                self.request.POST, self.request.FILES, prefix="gallery"
            )
            context["request"] = self.request
        else:
            gallery_form_set = GalleryFormSet(prefix="gallery")

        context["crud_type"] = self.crud_type
        context["formset"] = gallery_form_set
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["crud_type"] = self.crud_type
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        gallery_form = context["formset"]

        if form.is_valid() and gallery_form.is_valid():
            # Create Album's object
            form.instance.user = self.request.user
            self.object = form.save(commit=False)
            self.object.user = form.instance.user
            self.object = form.save()

            for index, gform in enumerate(gallery_form):
                # Validate and add Gallery's images to Album
                title = gform.cleaned_data.get("title")
                image = gform.cleaned_data.get("image")
                if title and image:
                    gform.save()
                    image_obj = Gallery.objects.get(title=title)
                    self.object.images.add(image_obj)
                    form.save()
            return super().form_valid(form)
        return super().form_invalid(form)


class AlbumCreateView(CRUDView, CreateView):
    crud_type = "create"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AlbumUpdateView(CRUDView, UserPassesTestMixin, UpdateView):
    crud_type = "update"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_func(self):
        """ Test whether the album belongs to the current user"""
        album = self.get_object()
        if self.request.user == album.user:
            return True
        return False


class AlbumDeleteView(CRUDView, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy("core:index")
    template_name = "core/album_confirm_delete.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_func(self):
        """ Test whether the album belongs to the current user"""
        album = self.get_object()
        if self.request.user == album.user:
            return True
        return False
