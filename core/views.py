import re
from django.db.models import Q, Count
from django.contrib import messages
from django.http import HttpResponse
from django.utils.text import slugify
from .models import Gallery, Photo, Category
from django.contrib.auth.models import User, AnonymousUser
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


def get_current_user(request):
    if request.user.is_authenticated:
        return request.user


class HomeListView(ListView):
    model = Gallery
    template_name = "core/index.html"
    context_object_name = "galleries"
    paginate_by = 12

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Query Gallery album based on its public status.
            # If the gallery belongs to the logged in, disregard "public" state
            # include his/her private galleries as well.
            # This will also fix any pagination error when logic occured in template.
            qs = Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        qs = Gallery.objects.filter(public=True)

        # Preform lookup searches in all Gallery's related field
        search = self.request.GET.get("q")

        if search:
            qs = Gallery.objects.query_search(search, qs)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # top 10 category used
        context["by_search"] = self.request.GET.get("q", False)
        context["top_category"] = Category.objects.annotate(
            c=Count("gallery")
        ).order_by("-c")[:10]


        page = self.request.GET.get("page")
        #     qs = paginator.page(1)



class GalleryDetailView(DetailView):
    model = Gallery
    template_name = "core/gallery_detail.html"
    context_object_name = "gallery"
    slug_url_kwarg = "slug"

    # Throws 404 if gallery is private
    def get_queryset(self):
        # Filtering gallery base on ownership and its public status.
        # This will return a gallery if it is access by "non_owner" AND it is "public"
        #  or if it's access by owner, then disregard the gallery's "public" status.
        return Gallery.objects.filter(
            Q(public=True) | Q(user=get_current_user(self.request))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_gallery = self.object.category.gallery_set

        if related_gallery.exists():
            # Filter galleries by creator or its public status

            # Include all public or galleries belonging to the current user
            related_gallery = related_gallery.filter(
                Q(public=True) | Q(user=get_current_user(self.request))
            )

            # Exclude the current gallery from the queryset
            related_gallery = related_gallery.exclude(name=self.object.name)

            # Limiting the total number of related_gallery to display in template
            related_gallery_total = related_gallery.count()
            if related_gallery_total >= 20:
                related_gallery = related_gallery[:20]

        context["photo_set"] = self.object.photo_set.all()
        context["related_gallery"] = related_gallery
        return context


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
    form_class = GalleryForm
    formset_class = GalleryFormSet

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

# PHOTO 
class PhotoDetailView(DetailView):
    model = Photo
    template_name = "core/photo_detail.html"
    context_object_name = "photo"
    slug_url_kwarg = "slug"

    # Throws 404 if photo gallery is private
    def get_queryset(self):
        return Photo.objects.filter(
            Q(gallery__public=True) | Q(gallery__user=get_current_user(self.request))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request,*args,**kwargs):
        self.object = self.get_object()
        self.object.views += 1   
        self.object.save()
        return super().get(request,*args,**kwargs)


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


