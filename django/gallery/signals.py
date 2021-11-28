from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.methods import resizeScale

from .models import Photo


@receiver(post_save, sender=Photo)
def resizePhoto(sender, created, instance, **kwargs):
    if created and instance.image:
        resizeScale(instance.image)


@receiver(post_save, sender=Photo)
def set_gallery_cover(sender, instance, **kwargs):
    """Set album cover from photos on save"""
    photos = instance.gallery.photos.filter(is_cover=True).exclude(pk=instance.id)
    if instance.is_cover:
        for photo in photos:
            photo.is_cover = False
            photo.save()
