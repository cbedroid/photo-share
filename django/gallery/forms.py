import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe

from .models import Category, Gallery, Photo


class GalleryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        # Helper variable that user to pass the current Gallery's
        # form.instance to PhotoForm's clean method when Gallery is being updated.
        self.gallery_update_obj = kwargs.pop("gallery_update_obj", None)
        super().__init__(*args, **kwargs)

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

        # Using form instance id to determine if a form is being updated or created.
        gallery_obj = Gallery.objects.filter(name__iexact=name, user=self.request.user)

        if self.instance.id:
            # Adding gallery uniqueness per user.
            gallery_obj = gallery_obj.exclude(pk=self.instance.id)
        if gallery_obj.exists():
            raise ValidationError("Sorry, This Gallery already exist!")
        return name


class PhotoForm(forms.ModelForm):
    IMAGE_PREVIEW = mark_safe(
        """
        <label class="photoset__image_label">
            <div><p class="image__label text-ellipsis font-bold text-gray-900 text-center py-4">add photo</p></div>
            <div class="image--wrapper">
                <img class="image form-image w-full" src="static/assets/add_image.png" style="height:200px;"/>
            </div>
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
        title = self.cleaned_data.get("title")
        if not title:
            raise ValidationError("Sorry, This photo must have a title")
        title = re.sub(r"\s{1,}", " ", title).strip()

        # NOTE: Only checking the photo title if the gallery form is being updated.
        #       Forms can be empty only if updating gallery, otherwise each field are required.
        gallery_id = self.instance.gallery_id
        if gallery_id:
            title_exist = Photo.objects.filter(title__iexact=title, gallery__pk=gallery_id)
            if title_exist.exists():
                raise ValidationError("Sorry, This image title is already taken")
        return title


GalleryFormSet = inlineformset_factory(
    Gallery,
    Photo,
    form=PhotoForm,
    fields=["title", "image", "is_cover"],
    extra=4,
)
