import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.utils.safestring import mark_safe

from .models import Category, Gallery, Photo


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ["name", "category", "public"]

    name = forms.CharField(
        required=True,
        label="Gallery name",
        widget=forms.TextInput(attrs={"placeholder": "Enter a gallery title"}),
    )
    category = forms.ModelChoiceField(
        label="category",
        empty_label="(Select Category)",
        widget=forms.Select,
        queryset=Category.objects.all(),
        required=True,
    )

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        name = re.sub(r"\s{1,}", " ", name).strip()

        # If form.instance then the form is being `updated` otherwise `created`.
        gallery_obj = Gallery.objects.filter(name__iexact=name)
        if self.instance:

            # Checking for gallery unique_together on field: `User.id and Gallery.name`
            gallery_obj = gallery_obj.exclude(name=self.instance.name)
        if gallery_obj.exists():
            raise ValidationError("Sorry, This Gallery already exist!")
        return name

    def save(self, commit=True, *args, **kwargs):
        return super(GalleryForm, self).save(commit=commit)


class PhotoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    IMAGE_PREVIEW = mark_safe(
        """
        <label class="photoset__image_label">
            <p class="image__label text-ellipsis font-bold text-gray-900 text-center py-4">add photo</p>
            <img class="image form-image w-full" src="static/assets/images/add_image.png" style="height:200px;"/>
        </label>"""
    )

    class Meta:
        model = Photo
        fields = "__all__"

    title = forms.CharField(
        required=True,
        label=False,
        widget=forms.TextInput(attrs={"placeholder": "Image title", "class": "photo-form text-center"}),
    )
    image = forms.ImageField(required=True, label=IMAGE_PREVIEW, widget=forms.FileInput)

    def clean_title(self):
        # Gallery unique_together will be force here
        # on fields (<Photo.gallery.user>` and `<Photo.title>`)

        title = self.cleaned_data.get("title")
        if not title:
            raise ValidationError("Sorry, This photo must have a title")

        # NOTE: Only validating photo's title if the form is being updated.
        #       Required fields will be forced only when gallery is being created,
        #       otherwise empty fields can be deemed as valid fields.
        title = re.sub(r"\s{1,}", " ", title).strip()
        photos = Photo.objects.filter(gallery__user=self.user, title=title)
        if photos.exists():
            raise ValidationError("Sorry, That image title is already taken")
        return title


class BaseGalleryFormset(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        titles = []
        for form in self.forms:  # <-- formset's forms
            if self.can_delete and self._should_delete_form(form):
                continue

            title = form.cleaned_data.get("title")
            if title:
                titles.append(title)

        # Force Gallery creation to have at least one photo.
        if not self.instance.id and not titles:
            raise ValidationError("At least one photo must be added to your gallery")

    def save(self, commit=True):
        instance = super(BaseGalleryFormset, self).save(commit=False)
        instance.gallery = self.instance
        if commit:
            instance.save()
        return instance


GalleryFormSet = inlineformset_factory(
    Gallery,
    Photo,
    form=PhotoForm,
    formset=BaseGalleryFormset,
    fields=["title", "image", "is_cover"],
    extra=4,
    max_num=20,
)
