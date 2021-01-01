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

from .forms import (
    AlbumForm,
    GalleryForm,
)
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
        GalleryFormSet = formset_factory(GalleryForm, extra=3, min_num=0, max_num=3)

        if self.request.POST:
            gallery_form_set = GalleryFormSet(
                self.request.POST,
                self.request.FILES, 
                prefix="gallery"
            )
        else:
            gallery_form_set = GalleryFormSet(prefix="gallery")
            context["form_title"] = "Add New Album"
            context["current_albums"] = Album.objects.filter(
                user=self.request.user
            )

        context["formset"] = gallery_form_set
        return context

    def form_valid(self, form, *args, **kwargs):
        if form.is_valid():

            # Retrieve Gallery object from form context
            context = self.get_context_data()
            gallery_form = context["formset"]

            # Create Album's object
            form.instance.user = self.request.user
            self.object = form.save(commit=False)
            self.object.user = form.instance.user
            self.object = form.save()

            for gform in gallery_form:
                # Validate and add Gallery's images to Album
                if gform.is_valid():
                    title = gform.cleaned_data.get("title")
                    image = gform.cleaned_data.get("image")

                    if title and image:
                        image_obj = gform.save()
                        image_obj = Gallery.objects.get(title=image_obj.title)
                        self.object.images.add(image_obj)

        return super().form_valid(form)


class AlbumUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Album
    fields = ["name", "public"]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Update Album"
        context["current_albums"] = Album.objects.filter(
            user=self.request.user
         )
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
