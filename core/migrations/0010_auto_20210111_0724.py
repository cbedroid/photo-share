# Generated by Django 3.1.4 on 2021-01-11 07:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_auto_20210110_0726"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="photo",
            unique_together=set(),
        ),
    ]
