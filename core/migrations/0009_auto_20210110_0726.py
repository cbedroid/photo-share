# Generated by Django 3.1.4 on 2021-01-10 07:26

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0008_auto_20210110_0711"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="gallery",
            unique_together={("name", "user")},
        ),
        migrations.AlterUniqueTogether(
            name="photo",
            unique_together={("title", "gallery")},
        ),
    ]
