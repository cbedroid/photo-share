from django.db import models
from django.db.models.deletion import DO_NOTHING
from django.utils.translation import gettext_lazy as _
from simple_history import register


class PhotoShareBaseModel(models.Model):
    """Base Model for all models."""

    created = models.DateTimeField(auto_now_add=True, help_text="An ISO 8601 date time of when this was created")
    updated = models.DateTimeField(auto_now=True, help_text="An ISO 8601 date time of when this was last updated")

    class Meta:
        abstract = True


class FAQTopic(PhotoShareBaseModel):
    name = models.CharField(max_length=40)
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.name


class FAQ(PhotoShareBaseModel):
    """Frequently Asked Question"""

    topic = models.ForeignKey(FAQTopic, null=True, on_delete=DO_NOTHING)

    question = models.CharField(
        max_length=150,
        blank=False,
        help_text=_("Frequently asked question (150 max char) required"),
    )
    answer = models.TextField(
        max_length=500,
        blank=False,
        help_text=_("Frequently asked question's answer (500 max char) required"),
    )

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQS"


# ********************************#
# ---TRACK CHANGES IN MODELS ---- #
# ********************************#
register(FAQ)
