import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission
        django_get_or_create = ("codename",)


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    is_active = True
    is_superuser = False
    is_staff = False

    class Meta:
        model = User
        django_get_or_create = ("username",)

    @factory.post_generation
    def user_permissions(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.user_permissions.add(*extracted)
