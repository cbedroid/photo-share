# Generated by Django 3.2.9 on 2021-11-24 01:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gallery", "0003_alter_photo_gallery"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gallery",
            name="category",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="gallery", to="gallery.category"
            ),
        ),
        migrations.AlterField(
            model_name="gallery",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="gallery", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]