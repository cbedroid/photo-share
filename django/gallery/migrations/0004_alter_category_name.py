# Generated by Django 3.2.9 on 2021-12-02 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0003_auto_20211124_0640"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.IntegerField(
                choices=[
                    (0, "general"),
                    (1, "abstract"),
                    (2, "adventure"),
                    (3, "architectural"),
                    (4, "art"),
                    (5, "black and white"),
                    (6, "business"),
                    (7, "candid"),
                    (8, "cityscape"),
                    (9, "commercial"),
                    (10, "composite"),
                    (11, "creative"),
                    (12, "documentary"),
                    (13, "drone"),
                    (14, "double-exposure"),
                    (15, "editorial"),
                    (16, "event"),
                    (17, "family"),
                    (18, "fashion"),
                    (19, "film"),
                    (20, "fine art"),
                    (21, "food"),
                    (22, "golden hour"),
                    (23, "holiday"),
                    (24, "indoor"),
                    (25, "infrared"),
                    (26, "landscape"),
                    (27, "lifestyle"),
                    (28, "long exposure"),
                    (29, "musical"),
                    (30, "milky way"),
                    (31, "minimalist"),
                    (32, "newborn"),
                    (33, "night"),
                    (34, "pet"),
                    (35, "portrait"),
                    (36, "product"),
                    (37, "real estate"),
                    (38, "seascape"),
                    (39, "social media"),
                    (40, "sports"),
                    (41, "still-life"),
                    (42, "surreal"),
                    (43, "street"),
                    (44, "time-lapse"),
                    (45, "travel"),
                    (46, "underwater"),
                    (47, "urban exploration"),
                    (48, "war"),
                    (49, "wedding"),
                    (50, "wildlife"),
                ],
                db_index=True,
                default=0,
                unique=True,
            ),
        ),
    ]