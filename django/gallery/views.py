import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Sum
from django.http.response import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.list import MultipleObjectMixin

from .mixins import GalleryFormMixin, UserAccessPermissionMixin
from .models import Category, Gallery, Photo


class GalleryDetailView(DetailView, MultipleObjectMixin):
    model = Gallery
    template_name = "gallery/gallery_detail.html"
    object_list = None
    paginate_by = 25

    # Throws 404 if gallery is private
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        else:
            return Gallery.objects.filter(public=True)

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        object_list = obj.photos.order_by("-pk")
        context = super().get_context_data(object_list=object_list, **kwargs)
        related_gallery = self.object.category.gallery
        user = self.request.user
        if related_gallery.exists():
            # Filter galleries by owner or its public state
            # Only display galleries if user is the owner or gallery is public
            if user.is_authenticated:
                related_gallery = related_gallery.filter(
                    Q(public=True) | Q(user=self.request.user),
                ).exclude(pk=self.object.pk)
            else:
                related_gallery = related_gallery.filter(public=True).exclude(pk=self.object.pk)

        context["related_gallery"] = related_gallery[:20]
        context["is_user"] = obj.user == self.request.user
        context["cover_photo"] = obj.photos.filter(is_cover=True).last()
        return context


class GalleryListView(ListView):
    model = Gallery
    template_name = "gallery/gallery_list.html"
    paginate_by = 25

    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        else:
            qs = Gallery.objects.filter(public=True)

        search = self.request.GET.get("q")
        if search:
            return Gallery.objects.query_search(search, qs)

        # TODO order by datetime range  - one to two week newest
        return qs.annotate(photo_views=Sum("photos__views")).order_by("?", "-photo_views")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show top 20 trending category
        context["by_search"] = self.request.GET.get("q", False)
        context["top_category"] = Category.objects.alias(c=Count("gallery")).order_by("-c")[:20]
        return context


class GalleryCreateView(GalleryFormMixin, CreateView):
    model = Gallery
    login_url = reverse_lazy("account_login")
    template_name = "gallery/gallery_form.html"
    object = None

    def get_success_url(self, *args, **kwargs):
        return self.object.get_absolute_url()


class GalleryUpdateView(GalleryFormMixin, UserPassesTestMixin, UpdateView):
    model = Gallery
    login_url = reverse_lazy("account_login")
    template_name = "gallery/gallery_form.html"
    object = None

    def test_func(self):
        """Test whether the Gallery belongs to the current user"""
        return self.request.user == self.get_object().user

    def get_success_url(self, *args, **kwargs):
        return self.get_object().get_absolute_url()


class GalleryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Gallery
    template_name = "galle(ry/gallery_confirm_delete.html"
    login_url = reverse_lazy("account_login")
    success_url = reverse_lazy("core:index")

    def test_func(self):
        """Test whether the Gallery belongs to the current user"""
        return self.request.user == self.get_object().user


# PHOTO
class PhotoDetailView(UserAccessPermissionMixin, DetailView):
    model = Photo
    template_name = "gallery/photo_detail.html"
    context_object_name = "photo"
    slug_url_kwarg = "slug"

    # Throws 404 if photo gallery is private
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Photo.objects.filter(Q(gallery__public=True) | Q(gallery__user=self.request.user))
        else:
            return Photo.objects.filter(gallery__public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["is_user"] = obj.gallery.user == self.request.user
        return context

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.views += 1
        self.object.save()
        context = self.get_context_data()
        return self.render_to_response(context)


class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Photo
    template_name = "gallery/photo_confirm_delete.html"

    def test_func(self):
        """Test whether the Photo belongs to the current user"""
        user = self.get_object().gallery.user
        return user == self.request.user

    def get_success_url(self, *args, **kwargs):
        gallery = self.object.gallery
        if gallery.photos.count() > 1:
            return gallery.get_absolute_url()
        return reverse("core:index")

    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        gallery = self.object.gallery
        if gallery.photos.count() == 0:
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


class PhotoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Photo
    login_url = "account_login"

    def test_func(self):
        """Test whether the Photo belongs to the current user"""
        user = self.get_object().gallery.user
        return user == self.request.user

    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            response = {"status": False}
            obj = self.get_object()
            data = json.loads(self.request.body)
            obj.is_cover = data.get("cover")
            obj.save()
            response["status"] = True
            return JsonResponse(response)
        super().post(*args, **kwargs)


class CategoryDetailView(DetailView):
    slug_url_kwarg = "slug"
    pass
