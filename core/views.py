import re
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import GalleryForm, PhotoForm, GalleryFormSet
from .models import Gallery, Photo
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)


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
            return Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        return Gallery.objects.filter(public=True)


class GalleryDetailView(DetailView):
    model = Gallery
    template_name = "core/gallery_detail.html"
    context_object_name = "gallery"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        return Gallery.objects.filter(public=True)


class CRUDView(LoginRequiredMixin):
    model = Gallery
    form_class = GalleryForm
    template_name = "core/gallery_form.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            gallery_form_set = GalleryFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="photo",
            )
            context["request"] = self.request

        else:
            gallery_form_set = GalleryFormSet(
                prefix="photo",
                queryset=Gallery.objects.none(),
            )

        context["formset"] = gallery_form_set
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["gallery_update_obj"] = self.object
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        # Create Gallery's object
        # Add user and save the Gallery object
        form.instance.user = self.request.user
        self.object = form.save()

        # Check all formset for validation
        for subform in formset:
            if subform.is_valid():
                title = subform.cleaned_data.get("title")
                image = subform.cleaned_data.get("image")
                if image and title:
                    subform.instance.gallery = self.object
                    subform.save()
            else:
                return super().form_invalid(form)

        return super().form_valid(form)


class GalleryCreateView(CRUDView, CreateView):
    model = Gallery
    form_class = GalleryForm
    template_name = "core/gallery_form.html"


class GalleryUpdateView(CRUDView, UserPassesTestMixin, UpdateView):
    def test_func(self):
        """ Test whether the Gallery belongs to the current user"""
        gallery = self.get_object()
        return self.request.user == gallery.user


class GalleryDeleteView(CRUDView, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy("core:index")
    template_name = "core/gallery_confirm_delete.html"

    def test_func(self):
        """ Test whether the Gallery belongs to the current user"""
        gallery = self.get_object()
        return self.request.user == gallery.user
