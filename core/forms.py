import re
from django import forms
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from .models import Album, Gallery


class AlbumForm(forms.ModelForm):
    def __new__(cls, *args, **kwargs):
        cls.request = kwargs.pop("request", None)
        cls.crud_type = kwargs.pop("crud_type", None)
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.crud_type = kwargs.pop("crud_type", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Album
        fields = ["name", "public"]

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        data = re.sub(r"\s{1,}", " ", name).strip()

        """ 
            Adding Album uniqueness here in clean's method instead 
            of adding it to the Album model.

            This way each users can have an album with the same name as other users,
            but each user can only have one album with a specific name
            Data cleaning will be handle by Model's form class
        """
        album = Album.objects.filter(name__iexact=data)
        if self.crud_type == "create" and album.exists():
            raise ValidationError("Sorry, This album already exists!")
        return data

    def save(self, commit=True):
        data = super().save(commit=False)
        if commit:
            form = super().save(commit=True)
            self.save_m2m()
        return data


class GalleryBaseFormSet(forms.BaseFormSet):
    titles = []

    def clean(self):
        if any(self.errors):
            return

        for index, form in enumerate(self.forms):
            title = form.cleaned_data.get("title")
            image = form.cleaned_data.get("iamge")
            self.titles.append(title)


class GalleryForm(forms.ModelForm):
    custom_label = """
        <label class="image-label">
            <div class="img__upload-wrapper">
                <img class="img-fluid" src="https://icon-library.net/images/upload-photo-icon/upload-photo-icon-21.jpg"/>
            </div>
            <div> <p class="image-label__custom">upload</p></div>
        </label>"""

    class Meta:
        model = Gallery
        fields = "__all__"

    title = forms.CharField(
        required=False,
        label=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Image title", "class": "text-center"}
        ),
    )
    image = forms.ImageField(required=False, label=custom_label, widget=forms.FileInput)

    def clean(self):
        data = super().clean()
        titles = GalleryBaseFormSet.titles
        user = AlbumForm.request.user
        title = data.get("title", None)
        image = data.get("image", None)

        if title:
            title = re.sub(r"\s{1,}", " ", title).strip()
            title_exist = Album.objects.filter(images__title=title, user=user)
            if title_exist.exists():
                raise ValidationError("Sorry, This image title is already taken")

        if image is None and title:
            raise ValidationError("No image found")

        if image and not title:
            print("Validation Image Not title")
            raise ValidationError("Image missing title")
        return data

    def save(self, commit=True):
        data = super().save(commit=False)
        if commit:
            data = super().save(commit=True)
        return data
