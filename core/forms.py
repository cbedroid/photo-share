import re
from django import forms
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory
from .models import Gallery, Photo, Category


class GalleryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        # Helper variable that user to pass the current Gallery's
        # form.instance to PhotoForm's clean method when Gallery is updating
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

    # def clean_category(self):
    #     category = self.cleaned_data.get("category")
    #     obj = Category.objects.filter(name=category)
    #     if obj.exists():
    #         return obj.first()
    #     raise ValidationError("Sorry, That category does not exist!")

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        name = re.sub(r"\s{1,}", " ", name).strip()

        """ 
            Adding Gallery uniqueness here in clean's method instead 
            of adding it to the Gallery model.

            This way each users can have an Gallery with the same name as other users,
            but each user can only have one Gallery with a specific name
            Data cleaning will be handle by Model's form class
        """
        # Added uniqueness for user here
        gallery_obj = Gallery.objects.filter(name__iexact=name, user=self.request.user)
        if self.instance.id:
            # Exclude form instance itself from existing queryset
            gallery_obj = gallery_obj.exclude(pk=self.instance.id)

        # If form does not have an id, then a new Gallery is being created,
        #  otherwise it being updated.
        if gallery_obj.exists():
            raise ValidationError("Sorry, This Gallery already exist!")
        return name


class PhotoForm(forms.ModelForm):
    CUSTOM_IMAGE_LABEL = """
        <label class="photoset__image_label">
            <div class="image--wrapper">
                <img class="image form-image " src="https://icon-library.net/images/upload-photo-icon/upload-photo-icon-21.jpg"/>
            </div>
            <div><p class="image__label text-ellipsis mt-1">upload</p></div>
        </label>"""

    class Meta:
        model = Photo
        fields = "__all__"

    title = forms.CharField(
        required=True,
        label=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Image title", "class": "photo-form text-center"}
        ),
    )
    image = forms.ImageField(
        required=True, label=CUSTOM_IMAGE_LABEL, widget=forms.FileInput
    )

    def clean_title(self):
        title = self.cleaned_data.get("title")

        if not title:
            raise ValidationError("Sorry, This photo must have a title")
        title = re.sub(r"\s{1,}", " ", title).strip()

        # Not checking Photo title if form does NOT have an instance id.
        # If there is no form id, then the form was called from CreateView,
        #  so the Gallery is here will be new.
        gallery_id = self.instance.gallery_id
        if gallery_id:
            # First, get the Gallery's object by pk
            # Check whether this gallery objects has
            #  a photo with this photo title
            #
            title_exist = Photo.objects.filter(
                title__iexact=title, gallery__pk=gallery_id
            )
            if title_exist.exists():
                raise ValidationError("Sorry, This image title is already taken")
        return title


GalleryFormSet = inlineformset_factory(
    Gallery,
    Photo,
    form=PhotoForm,
    fields=["title", "image"],
    extra=2,
)
