from django import forms


class ContactUsForm(forms.Form):
    MESSAGE_PLACEHOLDER = "How Can We Help You?"
    NAME_PLACEHOLDER = "Your Name"
    EMAIL_PLACEHOLDER = "Your Email"

    name = forms.CharField(
        required=True,
        max_length=120,
        widget=forms.TextInput(attrs={"class": "cf-name", "placeholder": NAME_PLACEHOLDER}),
    )

    email = forms.EmailField(
        required=True,
        max_length=80,
        widget=forms.TextInput(
            attrs={
                "class": "cf-email",
                "placeholder": EMAIL_PLACEHOLDER,
            }
        ),
    )
    message = forms.CharField(
        required=True,
        max_length=500,
        widget=forms.Textarea(attrs={"class": "cf-message", "placeholder": MESSAGE_PLACEHOLDER}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove annoying autofocus
        for field in self.fields:
            try:
                field.widget.attrs.pop("autofocus", None)
            except BaseException:
                pass
