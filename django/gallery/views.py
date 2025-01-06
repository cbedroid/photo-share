import json
from typing import TYPE_CHECKING, Optional, Union

from core.helpers import is_ajax_request
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, QuerySet
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .mixins import GalleryFormMixin, UserAccessPermissionMixin
from .models import Category, Gallery, Photo

if TYPE_CHECKING is True:
    from django.http import HttpRequest


class GalleryDetailView(DetailView):
    model = Gallery
    template_name = "gallery/gallery_detail.html"
    object_list = None
    paginate_by = 25

    # Throws 404 if gallery is private
    def get_queryset(self) -> QuerySet[Gallery]:
        qs = super().get_queryset()
        user = self.request.user
        filter_condition = Q(public=True)
        if user.is_authenticated:
            filter_condition |= Q(user=user)
        return qs.filter(filter_condition)

    def get_context_data(self, **kwargs) -> dict:
        current_user = self.request.user
        obj = self.get_object()
        related_gallery = obj.category.galleries
        photo_qs = obj.photos.all()

        context = super().get_context_data(object_list=photo_qs, **kwargs)
        if related_gallery:
            # Filter galleries by owner or its public state
            # Only display galleries if user is the owner or gallery is public
            if current_user.is_authenticated:
                related_gallery = related_gallery.filter(
                    Q(public=True) | Q(user=self.request.user),
                ).exclude(id=obj.id)
            else:
                related_gallery = related_gallery.filter(public=True).exclude(id=obj.id)

        context["related_gallery"] = related_gallery[:20]
        context["is_user"] = obj.user == current_user
        context["cover_photo"] = obj.cover_photo
        return context


class GalleryListView(ListView):
    model = Gallery
    template_name = "gallery/gallery_list.html"
    paginate_by = 25

    def get_queryset(self) -> QuerySet[Gallery]:
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            qs = qs.filter(Q(public=True) | Q(user=self.request.user))
        else:
            qs = qs.with_public_photos()

        search = self.request.GET.get("q")
        if search:
            return qs.query_search(search)

        # TODO order by datetime range  - one to two week newest
        return qs.with_total_views().order_by("?", "-total_views")

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # Show top 20 trending category
        context["by_search"] = self.request.GET.get("q", False)
        context["top_category"] = Category.objects.alias(total_galleries=Count("galleries")).order_by(
            "-total_galleries"
        )[:20]
        return context


class GalleryCreateView(GalleryFormMixin, CreateView):
    model = Gallery
    login_url = reverse_lazy("account_login")
    template_name = "gallery/gallery_form.html"
    object = None


class GalleryUpdateView(GalleryFormMixin, UserPassesTestMixin, UpdateView):
    model = Gallery
    login_url = reverse_lazy("account_login")
    template_name = "gallery/gallery_form.html"
    object = None

    def test_func(self) -> bool:
        """Test whether the Gallery belongs to the current user"""
        return self.request.user == self.get_object().user


class GalleryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Gallery
    template_name = "gallery/snippets/modals/gallery_confirm_delete.html"
    login_url = reverse_lazy("account_login")
    success_url = reverse_lazy("core:index")

    def test_func(self) -> bool:
        """Test whether the Gallery belongs to the current user"""
        return self.request.user == self.get_object().user


# PHOTO
class PhotoDetailView(UserAccessPermissionMixin, DetailView):
    model = Photo
    template_name = "gallery/photo_detail.html"
    context_object_name = "photo"
    slug_url_kwarg = "slug"

    # Throws 404 if photo gallery is private
    def get_queryset(self) -> QuerySet[Photo]:
        user = self.request.user
        qs = super().get_queryset()
        if user.is_authenticated:
            qs = qs.filter(Q(gallery__public=True) | Q(gallery__user=self.request.user))
        else:
            qs = qs.with_public_photos()
        return qs.all()

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        obj: Photo = self.get_object()
        context["is_user"] = obj.gallery.user == self.request.user
        context["galleries"] = Gallery.objects.filter(user=obj.gallery.user).exclude(pk=obj.gallery.pk)
        return context

    def get(self, *args, **kwargs) -> HttpResponse:
        obj = self.get_object()
        obj.views += 1
        obj.save()
        return super().get(*args, **kwargs)


class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Photo
    template_name = "gallery/photo_confirm_delete.html"

    def test_func(self) -> bool:
        """Test whether the Photo belongs to the current user"""
        user = self.get_object().gallery.user
        return user == self.request.user

    def get_success_url(self, *args, **kwargs) -> str:
        gallery = self.object.gallery
        if gallery.photos.count() > 1:
            return gallery.get_absolute_url()
        return reverse("core:index")

    def post(self, *args, **kwargs) -> HttpResponse:
        response = super().post(*args, **kwargs)
        gallery = self.object.gallery
        if gallery.photos.count() == 0:
            gallery.delete()
            messages.warning(
                self.request,
                f"Your gallery '{gallery}' was deleted, " "because it does not contain any photos",
            )
        return response


class PhotoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Photo
    login_url = "account_login"

    def test_func(self):
        """Test whether the Photo belongs to the current user"""
        user = self.get_object().gallery.user
        return user == self.request.user

    def post(self, request: "HttpRequest", *args, **kwargs) -> HttpResponse:
        if is_ajax_request(request):
            response = {"status": False}
            obj = self.get_object()
            data = json.loads(self.request.body)
            obj.is_cover = data.get("cover")
            obj.save()
            response["status"] = True
            return JsonResponse(response)
        return super().post(*args, **kwargs)


def photo_cover_update(request: "HttpRequest", pk: Optional[int] = None) -> Union[JsonResponse, HttpResponseRedirect]:
    """Update the cover photo of a gallery"""
    obj = get_object_or_404(Photo, pk=pk)
    owner = obj.gallery.user

    if request.user == owner and request.method == "POST":
        if is_ajax_request(request):
            data = json.loads(request.body)
            obj.is_cover = data.get("cover")
            obj.save(update_fields=("is_cover", "updated"))

            response = {"status": True}
            return JsonResponse(response)
    return redirect(".")


def photo_transfer(request: "HttpRequest", pk: Optional[int] = None) -> HttpResponseRedirect:
    """Transfer a photo to another gallery"""

    obj = Photo.objects.get(pk=pk)
    new_gallery = request.POST.get("gallery")
    if new_gallery:
        new_gallery_id = int(new_gallery)
        gallery = get_object_or_404(Gallery, id=new_gallery_id)
        gallery_detail_url = gallery.get_absolute_url()

        # Assign photo to a new gallery
        obj.gallery = gallery
        obj.save(update_fields=("gallery", "updated"))
        return redirect(gallery_detail_url)

    messages.warning(request, "Sorry, the gallery you are trying to transfer does not exist")
    return redirect(obj.get_absolute_url())


class CategoryDetailView(DetailView):
    slug_url_kwarg = "slug"
