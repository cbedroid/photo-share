from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.list import MultipleObjectMixin

from .forms import GalleryForm, GalleryFormSet
from .models import Category, Gallery, Photo


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
            # This will also fix any pagination error when logic occurred in template.
            qs = Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        qs = Gallery.objects.filter(public=True)

        # Preform lookup searches in all Gallery's related field
        search = self.request.GET.get("q")
        if search:
            qs = Gallery.objects.query_search(search, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # top 10 category used
        context["by_search"] = self.request.GET.get("q", False)
        context["top_category"] = Category.objects.alias(c=Count("gallery")).order_by("-c")[:10]
        return context


class CRUDMixin(LoginRequiredMixin):
    model = Gallery
    form_class = GalleryForm
    formset_class = GalleryFormSet
    template_name = "core/gallery_form.html"
    object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            context["form"] = self.form_class(instance=self.object)
            context["formset"] = self.formset_class(
                prefix="photo",
                queryset=Gallery.objects.none(),
            )
        else:
            context["form"] = self.form_class(instance=self.object)
            context["formset"] = self.formset_class(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="photo",
            )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["gallery_update_obj"] = self.object
        return kwargs

    def form_valid(self, form):
        # Add user and save the Gallery object
        context = self.get_context_data()
        formset = context.get("formset")
        form.instance.user = self.request.user
        # get gallery form, do not save until formset are valid
        self.object = form.save(commit=False)

        # Validate all formset are valid
        if not form.is_valid() or not formset.is_valid():
            context["form"] = form
            return super().form_invalid(form)

        # iterate through formset and save photo
        self.object = form.save()
        if formset.has_changed():
            for subform in formset:
                subform.full_clean()
                if not subform.is_valid():
                    return super().form_invalid(form)
                title = subform.cleaned_data.get("title")
                image = subform.cleaned_data.get("image")
                if image and title:
                    subform.instance.gallery = self.object
                    subform.save()
        return super().form_valid(form)


class GalleryDetailView(DetailView, MultipleObjectMixin):
    model = Gallery
    template_name = "core/gallery_detail.html"
    slug_url_kwarg = "slug"
    object_list = None
    paginate_by = 25

    # Throws 404 if gallery is private
    def get_queryset(self):
        # Filtering gallery base on ownership and its public status.
        # This will return a gallery if it is access by "non_owner" AND it is "public"
        #  or if it's access by owner, then disregard the gallery's "public" status.
        user = self.request.user
        if user.is_authenticated:
            return Gallery.objects.filter(Q(public=True) | Q(user=self.request.user))
        else:
            return Gallery.objects.filter(public=True)

    def get_context_data(self, **kwargs):
        object_list = self.object.photos.order_by("-pk")
        context = super().get_context_data(object_list=object_list, **kwargs)
        related_gallery = self.object.category.gallery_set
        user = self.request.user
        if related_gallery.exists():
            # Filter galleries by creator or its public status
            # Include all public or galleries belonging to the current user
            if user.is_authenticated:
                related_gallery = related_gallery.filter(
                    Q(public=True) | Q(user=self.request.user),
                ).exclude(pk=self.object.pk)
            else:
                related_gallery = related_gallery.filter(public=True).exclude(pk=self.object.pk)

        context["related_gallery"] = related_gallery[:20]
        return context


class GalleryCreateView(CRUDMixin, CreateView):
    model = Gallery

    def get_success_url(self, *args, **kwargs):
        return self.object.get_absolute_url()


class GalleryUpdateView(CRUDMixin, UserPassesTestMixin, UpdateView):
    model = Gallery

    def test_func(self):
        """Test whether the Gallery belongs to the current user"""
        return self.request.user == self.get_object().user

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context.get("formset")
        if form.is_valid():
            self.object = form.save()
            # since we are using gallery name as slug and
            # slug as lookup field for this view,
            # we have to catch gallery name changes here
            self.success_url = self.object.get_update_url()

            # check whether images were added during update
            if formset.has_changed():
                formset.full_clean()
                # if images were added but failed, then fail all forms!
                if not formset.is_valid():
                    context["formset"] = formset
                    return super().form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return self.get_object().get_absolute_url()


class GalleryDeleteView(CRUDMixin, UserPassesTestMixin, DeleteView):
    model = Gallery
    template_name = "core/gallery_confirm_delete.html"
    success_url = reverse_lazy("core:index")

    def test_func(self):
        """Test whether the Gallery belongs to the current user"""
        return self.request.user == self.get_object().user


# PHOTO
class PhotoDetailView(DetailView):
    model = Photo
    template_name = "core/photo_detail.html"
    context_object_name = "photo"
    slug_url_kwarg = "slug"

    # Throws 404 if photo gallery is private
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Photo.objects.filter(Q(gallery__public=True) | Q(gallery__user=self.request.user))
        else:
            return Photo.objects.filter(gallery__public=True)

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.views += 1
        self.object.save()
        context = self.get_context_data()
        return self.render_to_response(context)


class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Photo
    template_name = "core/photo_confirm_delete.html"
    pk_kwargs = "pk"

    def test_func(self):
        """Test whether the Photo belongs to the current user"""
        photo = self.get_object()
        return self.request.user == photo.gallery.user

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
