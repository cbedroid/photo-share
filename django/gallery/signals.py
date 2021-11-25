from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

from .models import Photo


@receiver(post_save, sender=Photo)
def resizeImage(sender, created, instance, **kwargs):
    """Resize large uploaded image"""
    """
     Scaling images will help reduce load time on the server and client.
     Pros:
        - Reduce client side load time. Images will load faster in client's browser.
        - Reduce storage's costs using cloud base services such as AWS S3 Bucket.
        - Improve overall UI Deign, making images uniformed throughout the entire website.
    Cons:
        - Slight tradeoff in load time, being that all image will be rescaled on every upload.
          This would add an additional load on the server, but the end results will highly
          outweights this small computation time.
    """
    try:
        if created:
            if instance.image:
                image = Image.open(instance.image.path)
                if image.width > 400 or image.height > 300:
                    output_size = (400, 300)
                    image = image.resize(output_size, Image.ANTIALIAS)
                    image.save(instance.image.path)
    except:  # noqa
        pass


@receiver(post_save, sender=Photo)
def set_gallery_cover(sender, instance, **kwargs):
    """Set album cover from photos on save"""
    photos = instance.gallery.photos.filter(is_cover=True).exclude(pk=instance.id)
    if instance.is_cover:
        for photo in photos:
            photo.is_cover = False
            photo.save()
