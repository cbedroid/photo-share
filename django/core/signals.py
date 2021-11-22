from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from PIL import Image

from .models import Photo


@receiver(post_save, sender=Photo)
def resizeImage(sender, instance, **kwargs):
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
        if instance.image:
            image = Image.open(instance.image.path)
            if image.width > 400 or image.height > 300:
                output_size = (400, 300)
                image = image.resize(output_size, Image.ANTIALIAS)
                image.save(instance.image.path)
    except:  # noqa
        pass


@receiver(post_save, sender=Photo)
def set_gallery_cover(sender, instance, created, **kwargs):
    """Set photo album cover to newly create photo image"""
    print("Updated album Cover")
    if created:
        photos = instance.gallery.photos.all()
        for photo in photos:
            photo.is_cover = False
        instance.is_cover = True  # set the current photo as the cover
        instance.save()
