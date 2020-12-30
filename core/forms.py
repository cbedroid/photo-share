import re
from django import forms
from django.utils.html import mark_safe
from django.conf import settings
from .models import Album,Gallery

class ImageUploadWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        # Create custom image file upload  button

        image_src  = "".join((settings.MEDIA_URL,'gallery/default_upload.png'))
        if value and getattr(value, "url", None):
            # This method is called only when updating Album.
            # Overwrite custom upload image src and add image's current source
            image_src = value.url

        return  mark_safe(
            f'''
            <div class="image-upload">
                <label for="file-input">
                    <img class="image__thumbnail" src="{image_src}" />
                </label>
                <input id="file-input" type="file" style="display:none"/>
                </div>
            '''
            )


class GalleryFormSet(forms.BaseFormSet):
    def clean(self):
        titles = []
        for form in self.forms:
            # Clean the gallery image data
            title = form.cleaned_data.get('title','')
            title = re.sub(r"\s{1,}", " ", title).strip()

            # Determine whether the image title is already being used
            # Two (2) Validaition Checks:
            #  1. Check whether the form itself contains the same image title.
            #  2. Check whether the database contains an image with the same title.
            title_exist = Gallery.objects.filter(title__iexact=title).exists()
            if titles in titles or title_exist :
                raise ValidationError('Sorry, This image title is already taken')
            titles.append(title)

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title','image']

        custom_image = forms.ImageField(
            widget= ImageUploadWidget
         )


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["name", "public"]

    def clean_name(self, *args, **kwargs):
        name = self.cleaned_data.get("name","")
        data = re.sub(r"\s{1,}", " ", name).strip()

        # Adding Album uniqueness here in validation instead 
        # of adding it to the Album model.

        # This way each users can have an album with the same name as other users,
        # but each user can only have one album with particular name
        # Data cleaning will be handle by Model's form class
        album = Album.objects.filter(name__iexact=data)
        if album.exists():
            raise ValidationError('Sorry, This album already exists!')

        return data
    
    # def save(self, commit=True):
    #     user = super(RegistrationForm, self).save(commit=False)
    #     user.username = self.cleaned_data["username"]
    #     user.email = self.cleaned_data["email"]
    #     user.subscribed = self.cleaned_data["subscribed"]
    #     if commit:
    #         user.save()
    #     return user


