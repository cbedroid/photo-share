import re
from django.db.models import Q
from django.contrib import messages
from .models import Gallery, Photo
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from .forms import GalleryForm, PhotoForm, GalleryFormSet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
    slug_url_kwarg = "slug"

    # Throws 404 if gallery is private

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Filtering gallery base on ownership and its public status.
            # This will return a gallery if it is access by "non_owner" AND it is "public"
            #  or if it's access by owner, then disregard the gallery's "public" status.
            return Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        return Gallery.objects.filter(public=True)


class CRUDView(LoginRequiredMixin):
    model = Gallery
    form_class = GalleryForm
    template_name = "core/gallery_form.html"
    object = None

    def get_context_data(self, *args, **kwargs):
        # NOTE: Removed code conjuction and added it to the  proper view
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["gallery_update_obj"] = self.object
        return kwargs

    def form_valid(self, form, formset):
        context = self.get_context_data()
        # Add user and save the Gallery object
        form.instance.user = self.request.user
        self.object = form.save()

        # Validate all formset
        for subform in formset:
            if subform.is_valid():
                title = subform.cleaned_data.get("title")
                image = subform.cleaned_data.get("image")
                if image and title:
                    subform.instance.gallery = self.object
                    subform.save()

        return super().form_valid(form)

    def form_invalid(self, form, formset):
        context = self.get_context_data()
        context["form"] = form
        context["formset"] = formset
        return self.render_to_response(context)

    def test_func(self):
        """ Test whether the Gallery belongs to the current user"""
        gallery = self.get_object()
        return self.request.user == gallery.user


class GalleryCreateView(CRUDView, CreateView):
    model = Gallery
    object = None
    form_class = GalleryForm
    formset_class = GalleryFormSet
    template_name = "core/gallery_form.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = self.get_form()
        context["form"] = form
        context["formset"] = GalleryFormSet(
            prefix="photo",
            queryset=Gallery.objects.none(),
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = self.get_form()
        formset = GalleryFormSet(
            request.POST,
            request.FILES,
            instance=self.object,
            prefix="photo",
        )
        context["form"] = form
        context["formset"] = formset

        if form.is_valid() and formset.is_valid():
            # Only allow users to create gallery if formset is valid
            # This way there wil be no empty galleries.
            return self.form_valid(form, formset)
        return self.render_to_response(context)


class GalleryUpdateView(CRUDView, UserPassesTestMixin, UpdateView):
    def test_func(self):
        """ Test whether the Gallery belongs to the current user"""
        gallery = self.get_object()
        return self.request.user == gallery.user

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        form = self.get_form()
        context["form"] = form
        context["formset"] = GalleryFormSet(
            prefix="photo",
            queryset=Gallery.objects.none(),
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        form = self.get_form()
        formset = GalleryFormSet(
            request.POST,
            request.FILES,
            instance=self.object,
            prefix="photo",
        )
        context["form"] = form
        context["formset"] = formset

        if form.is_valid():
            # check whether images were added during update
            if formset.has_changed():
                formset.full_clean()
                # if images were added but failed, then fail all forms!
                if not formset.is_valid():
                    return self.form_invalid(form, formset)
                return self.form_valid(form, formset)
            elif form.has_changed():
                # If only the current gallery object name was changed
                # then valid it and return the validated response
                return self.form_valid(form, formset)
        return self.render_to_response(context)


class GalleryDeleteView(CRUDView, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy("core:index")
    template_name = "core/gallery_confirm_delete.html"


class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Photo
    template_name = "core/photo_confirm_delete.html"
    pk_kwargs = "pk"

    def get_success_url(self, *args, **kwargs):
        gallery = self.object.gallery
        if gallery.photo_set.count() > 1:
            return reverse(
                "core:gallery-detail",
                kwargs={"slug": gallery.slug, "owner": slugify(gallery.user.username)},
            )
        else:
            return reverse("core:index")

    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        gallery = self.object.gallery
        if gallery.photo_set.count() == 0:
            gallery.delete()
            messages.warning(
                self.request,
                "".join(
                    (
                        f'Your gallery "{gallery}" was deleted,',
                        " because it does not contain any photos",
                    )
                ),
            )
        return response

    def test_func(self):
        """ Test whether the Photo belongs to the current user"""
        photo = self.get_object()
        return self.request.user == photo.gallery.user
