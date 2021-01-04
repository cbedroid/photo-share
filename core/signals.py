import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Gallery


@receiver(post_delete, sender=Gallery)
def removeDeleteGallery(sender, instance, **kwargs):
    """ Deletes Image file from filesystem """
    try:
        if instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
    except:
        pass
