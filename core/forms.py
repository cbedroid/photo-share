import re
from django import forms
from .models import Album


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["name", "public"]

    image = forms.ImageField(
        error_messages={"invalid": "Opps, File must be an image file only"},
        widget=forms.FileInput,
    )

    def clean_name(self, *args, **kwargs):
        # user = self.request.user
        print(f"\nARGS: {args} KWARGS: {kwargs}")

        name = self.cleaned_data["name"]
        data = re.sub(r"\s{1,}", " ", name).strip()
        return data
