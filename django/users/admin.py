from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class UserEmailRequiredMixin(object):
    """Mixin that force email address to be required on Admin User's forms"""

    def __init__(self, *args, **kwargs):
        super(UserEmailRequiredMixin, self).__init__(*args, **kwargs)
        self.fields["email"].required = True


class UserCreationForm(UserEmailRequiredMixin, UserCreationForm):
    pass


class UserChangeForm(UserEmailRequiredMixin, UserChangeForm):
    pass


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "username",
        "last_name",
        "first_name",
        "email",
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = dict(super().get_fieldsets(request, obj=obj))
        if "email" not in fieldsets[None]["fields"]:
            fieldsets[None]["fields"] = fieldsets[None]["fields"] + ("email",)

        return tuple((x, y) for x, y in fieldsets.items())


admin.site.register(User, UserAdmin)
