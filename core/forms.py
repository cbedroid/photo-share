import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Album, Gallery


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = "__all__"

    title = forms.CharField(
        required=False,
        label=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter Image title",
            }
        ),
    )
    image = forms.ImageField(required=False, label="Upload", widget=forms.FileInput)

    def clean_title(self):
        title = self.cleaned_data.get("title")
        title = re.sub(r"\s{1,}", " ", title).strip()
        title_exist = Gallery.objects.filter(title__iexact=title).exists()

        if title and title_exist:
            raise ValidationError("Sorry, This image title is already taken")
        self.cleaned_data.pop("title")
        return title

    def clean_image(self):
        image = self.cleaned_data.get("image")
        return image

    def save(self, commit=True):
        form = super().save(commit=False)
        if commit:
            form = super().save(commit=True)
        return form


class AlbumForm(forms.ModelForm):
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
        if album.exists():
            raise ValidationError("Sorry, This album already exists!")
        return data

    def save(self, commit=True):
        data = super().save(commit=False)
        if commit:
            form = super().save(commit=True)
            self.save_m2m()
        return data
