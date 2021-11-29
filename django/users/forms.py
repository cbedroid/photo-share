from allauth.account.forms import LoginForm
from django import forms
from django.conf import settings
from django.contrib.auth import forms as userforms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from profanity.validators import validate_is_profane

User = get_user_model()


class UserUpdateForm(userforms.UserChangeForm):
    password = None
    image = forms.ImageField(widget=forms.FileInput())

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "image",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate_name(self, data):
        # Check the name for profanity
        try:
            validate_is_profane(data)
        except ValidationError:
            # Note: Profanity is not converted into Django translation, so we add our own
            # Using except block to add translation to Profanity
            raise ValidationError(_("Please remove any profanity/bad words."))
        return data

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        return self.validate_name(first_name)

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        return self.validate_name(last_name)

    def save(self, commit=True, *args, **kwargs):
        instance = super(UserUpdateForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance


class UserSignUpForm(userforms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserSignUpForm, self).__init__(*args, **kwargs)
        # self.fields["captcha"].label = ""
        self.fields["username"].help_text = _(
            "Required. {} characters or fewer. Letters, digits and @/./+/-/_ only.".format(
                settings.ACCOUNT_USERNAME_MAX_LENGTH
            )
        )

    # captcha = ReCaptchaField(widget=ReCaptchaV3)
    class Meta:
        model = User
        # TODO Add captcha field "captcha"
        fields = ("username", "email")
        field_order = ["username", "email", "password"]

    def clean_username(self):
        username = self.cleaned_data["username"]

        # Check the username for profanity
        try:
            validate_is_profane(username)
        except ValidationError:
            # Note: Profanity is not converted into Django translation, so we add our own
            # Using except block to add translation to Profanity
            raise ValidationError(_("Please remove any profanity/bad words."))

        if len(username) > settings.ACCOUNT_USERNAME_MAX_LENGTH:
            raise ValidationError(
                _(
                    "Please enter a username value less than the {} characters".format(
                        settings.ACCOUNT_USERNAME_MAX_LENGTH
                    )
                )
            )
        try:
            user = User.objects.filter(username__iexact=username)
            if user.exists():
                raise ValidationError(_("Sorry, that username is already taken! "))
            return username
        except User.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.filter(email__iexact=email)
            if user.exists():
                raise ValidationError(_("A user is already registered with this e-mail address."))
            return email
        except User.DoesNotExist:
            return email

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(UserSignUpForm, self).save(request)
        return user


class UserLoginForm(LoginForm):
    pass


class AccountDeleteForm(forms.ModelForm):
    delete_account = forms.BooleanField(initial=False)
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "confirm-password"}),
        help_text=("Confirm password for your account"),
    )

    class Meta:
        model = User
        fields = ("delete_account", "password")

    def clean_password(self):
        """
        Validate that the password field is correct before deleting account.
        """
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise ValidationError(
                _("The password you enter was incorrect"),
                code="password_incorrect",
            )
        return password

    def save(self, commit=True):
        """Delete User Account"""
        if commit:
            self.user.delete()
        return self.user
