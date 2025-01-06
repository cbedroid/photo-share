from django.db.models.signals import post_save
from django.dispatch import receiver
from gallery.models import Photo
from utils.methods import resize_scale


@receiver(post_save, sender=Photo)
def resize_photo(sender, created: bool, instance: Photo, **kwargs):
    if created and instance.image:
        resize_scale(instance.image)


@receiver(post_save, sender=Photo)
def set_gallery_cover(sender, created: bool, instance: Photo, **kwargs):
    """Set album cover from photos on save"""
    photos = instance.gallery.photos
    if created and photos.count() == 1:
        # Save first and only photo as the gallery album cover
        instance.is_cover = True
        instance.save()
    elif instance.is_cover:
        # Update the current photo to the gallery cover and
        # set other all photo `is_cover` to False.
        photos.filter(is_cover=True).exclude(pk=instance.id).update(is_cover=False)
