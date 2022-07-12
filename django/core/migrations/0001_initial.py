# Generated by Django 4.0.6 on 2022-07-12 03:29

import simple_history.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FAQ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "question",
                    models.CharField(help_text="Frequently asked question (150 max char) required", max_length=150),
                ),
                (
                    "answer",
                    models.TextField(
                        help_text="Frequently asked question's answer (500 max char) required", max_length=500
                    ),
                ),
            ],
            options={
                "verbose_name": "FAQ",
                "verbose_name_plural": "FAQS",
            },
        ),
        migrations.CreateModel(
            name="FAQTopic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=40)),
                ("description", models.TextField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalFAQ",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                (
                    "question",
                    models.CharField(help_text="Frequently asked question (150 max char) required", max_length=150),
                ),
                (
                    "answer",
                    models.TextField(
                        help_text="Frequently asked question's answer (500 max char) required", max_length=500
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
            ],
            options={
                "verbose_name": "historical FAQ",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
