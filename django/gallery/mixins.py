from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect

from .forms import GalleryForm, GalleryFormSet
from .models import Gallery, Photo


class UserAccessPermissionMixin(PermissionRequiredMixin):
    def has_permission(self):
        """Verify whether Gallery is viewable by user"""
        user = self.request.user
        obj = self.get_object()
        # Check whether object is Gallery object
        # else object must be a Photo Object
        if not isinstance(obj, Gallery):
            assert obj.__class__ == Photo
            obj = obj.gallery

        # Only allow Gallery's owner to view private gallery
        return obj.public or user == obj.user


class GalleryFormMixin(LoginRequiredMixin):
    """Mixin handles Gallery Create and Update View"""

    model = Gallery
    form_class = GalleryForm
    formset_class = GalleryFormSet
    slug_url_kwarg = "slug"

    def get_object(self, **kwargs):
        try:
            return super().get_object(**kwargs)
        except:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        if self.request.method == "GET":
            context["form"] = self.form_class(instance=obj)
            context["formset"] = GalleryFormSet(
                queryset=Gallery.objects.filter(user=self.request.user),
                prefix="photo",
            )
        else:
            context["form"] = self.form_class(self.request.POST, instance=obj)
            context["formset"] = self.formset_class(
                self.request.POST,
                self.request.FILES,
                prefix="photo",
                instance=obj,  # <-- Needed for BaseGalleryFormSet. See forms
                form_kwargs={"user": self.request.user},
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context.get("formset")

        # Verify all form and formset are valid before saving
        if not form.is_valid() or not formset.is_valid():
            context["form"] = form
            context["formset"] = formset
            return super().form_invalid(form)

        #  Retrieve user object from gallery form
        form.instance.user = self.request.user

        if formset.has_changed():
            self.object = form.save(commit=False)
            # Iterate through formset and validated each photo fields individually
            for subform in formset:
                subform.instance.gallery = self.object
                subform.full_clean()

                # fail all forms immediately if any formset fails
                if not subform.is_valid():
                    return super().form_invalid(form)
                title = subform.cleaned_data.get("title")
                image = subform.cleaned_data.get("image")

                # Only save photo if it has both an image and title
                if image and title:
                    form.save()
                    subform.instance.gallery = self.object
                    subform.save()
        self.object = form.save()
        # return super().form_valid(form)
        return redirect(self.get_success_url())

    def get_success_url(self, *args, **kwargs):
        return self.object.get_absolute_url()
