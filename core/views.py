import re
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
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
from django.db.models import Q
from django.forms import formset_factory
from .models import Gallery, Photo


class HomeListView(ListView):
    model = Gallery
    template_name = "core/index.html"
    context_object_name = "galleries"
    paginate_by = 25
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            # This will also fix any pagination error when logic occured in template.
            return Gallery.objects.filter(
                    Q(public=True) | Q(user=self.request.user)
                )
        return Gallery.objects.filter(public=True)


class GalleryDetailView(DetailView):
    model = Gallery
    template_name = "core/gallery_detail.html"
    context_object_name = "gallery"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return  Gallery.objects.filter(Q(public=True) | Q(user=self.request.user) ) 
        return  Gallery.objects.filter(public=True)
        


class CRUDView(LoginRequiredMixin):
    model = Gallery
    form_class = AlbumForm
    template_name = "core/gallery_form.html"
    crud_type = "create"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        GalleryFormSet = formset_factory(
            GalleryForm, formset=GalleryBaseFormSet, extra=3
        )

        if self.request.POST:
            gallery_form_set = GalleryFormSet(
                self.request.POST, self.request.FILES, prefix="Photo"
            )
            context["request"] = self.request
        else:
            gallery_form_set = GalleryFormSet(prefix="Photo")

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
            # Create Gallery's object
            form.instance.user = self.request.user
            self.object = form.save(commit=False)
            self.object.user = form.instance.user
            self.object = form.save()

            for index, gform in enumerate(gallery_form):
                # Validate and add Photo's images to Gallery
                title = gform.cleaned_data.get("title")
                image = gform.cleaned_data.get("image")
                if title and image:
                    gform.save()
                    image_obj = Photo.objects.get(title=title)
                    self.object.images.add(image_obj)
                    form.save()
            return super().form_valid(form)
        return super().form_invalid(form)


class GalleryCreateView(CRUDView, CreateView):
    crud_type = "create"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GalleryUpdateView(CRUDView, UserPassesTestMixin, UpdateView):
    crud_type = "update"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_func(self):
        """ Test whether the Gallery belongs to the current user"""
        Gallery = self.get_object()
        if self.request.user == Gallery.user:
            return True
        return False


class GalleryDeleteView(CRUDView, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy("core:index")
    template_name = "core/gallery_confirm_delete.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_func(self):
        """ Test whether the Gallery belongs to the current user"""
        Gallery = self.get_object()
        if self.request.user == Gallery.user:
            return True
        return False
