from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.methods import resizeScale

from .models import Photo


@receiver(post_save, sender=Photo)
def resizePhoto(sender, created, instance, **kwargs):
    if created and instance.image:
        resizeScale(instance.image)


@receiver(post_save, sender=Photo)
def set_gallery_cover(sender, created, instance, **kwargs):
    """Set album cover from photos on save"""
    photos = instance.gallery.photos
    if created and photos.count() == 1:
        # Save first and only photo as the gallery album cover
        photo = photos.first()
        instance.is_cover = True
        instance.save()
    elif instance.is_cover:
        photos = photos.filter(is_cover=True).exclude(pk=instance.id)
        for photo in photos:
            photo.is_cover = False
            photo.save()
