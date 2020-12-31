import re
from django import forms
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
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

        image_id = attrs.get('id','file_input')
        return mark_safe(
            f'''
            <div class="image-upload__media">
                <label for="{image_id}_upload">
                    <img class="img__upload-thumbnail" src="{image_src}"/>
                </label>
                <p class="img__upload-label">Add an image</p>
                <input id="{image_id}_upload" type="file" style="display:none"/>
                </div>
            '''
            )



class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title','image']
    
    title = forms.CharField(required=False,
        label=False,
        widget=forms.TextInput(attrs={
            'placeholder':'Enter Image title',
        })
     )
    image = forms.ImageField(
        required=False,
        label=False,
        widget = ImageUploadWidget
    )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        print(f'Title:{title}\n')
        #title = form.cleaned_data.get('title','')
        title = re.sub(r"\s{1,}", " ", title).strip()

        # Determine whether the image title is already being used
        # Perform two (2) validation checks here:
        #  1. Check whether the form itself contains the same image title.
        #  2. Check whether the database contains an image with the same title.
        title_exist = Gallery.objects.filter(title__iexact=title).exists()
        if title_exist :
            raise ValidationError('Sorry, This image title is already taken')
        return title



class GalleryFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,**kwargs)

    def clean(self):
        super().clean()
        titles = []
        for form in self.forms:
            # Clean the gallery image data
            clean_data = form.clean()
            # print(f'\nFormDir: {dir(form)}\n')
            # title = cleaned_data.get('title')
            # image = cleaned_data.get('image')

            # print(f'Title:{title}\nImage: {image}\n')

            # #title = form.cleaned_data.get('title','')
            # title = re.sub(r"\s{1,}", " ", title).strip()

            # # Determine whether the image title is already being used
            # # Perform two (2) validation checks here:
            # #  1. Check whether the form itself contains the same image title.
            # #  2. Check whether the database contains an image with the same title.
            # title_exist = Gallery.objects.filter(title__iexact=title).exists()
            # if titles in titles or title_exist :
            #     raise ValidationError('Sorry, This image title is already taken')
            # titles.append(title)


class AlbumForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        super().__init__(*args,**kwargs)

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
    
    def save(self, commit=True):
        form = super().save(commit=False)
        # user.username = self.cleaned_data["username"]
        # user.email = self.cleaned_data["email"]
        # user.subscribed = self.cleaned_data["subscribed"]
        # if commit:
        #     user.save()
        # return user


