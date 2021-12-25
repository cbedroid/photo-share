# Generated by Django 3.2 on 2021-12-24 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_remove_user_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="image",
            field=models.ImageField(blank=True, help_text="user profile image ", null=True, upload_to="users"),
        ),
    ]