import os

import factory
from django.conf import settings
from django.utils.text import slugify
from gallery.enums import GalleryCategory, GalleryCategoryColor
from users.factories import UserFactory


class CategoryFactory(factory.django.DjangoModelFactory):
    name = GalleryCategory.GENERAL
    label = GalleryCategoryColor.BLACK_WHITE
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))

    class Meta:
        model = "gallery.Category"


class GalleryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    category = factory.SubFactory(CategoryFactory)
    user = factory.SubFactory(UserFactory)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    public = True

    class Meta:
        model = "gallery.Gallery"


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda obj_id: f"tag-{obj_id}")

    class Meta:
        model = "gallery.Tag"


class PhotoFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("word")
    gallery = factory.SubFactory(GalleryFactory)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    is_cover = False
    image = factory.django.ImageField(
        from_path=os.path.join(settings.BASE_DIR, "tests/images/test_image.jpg"),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    class Meta:
        model = "gallery.Photo"
        django_get_or_create = ("gallery",)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.tags.add(*extracted)
