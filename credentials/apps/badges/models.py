"""
Badges DB models.
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from credentials.apps.credentials.models import AbstractCredential


class BadgeTemplate(AbstractCredential):
    """
    Describes badge credential type.
    """

    TYPE = "openedx"

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, help_text=_("Unique badge template ID."))
    name = models.CharField(max_length=255, help_text=_("Badge template name."))
    description = models.TextField(null=True, blank=True, help_text=_("Badge template description."))
    icon = models.ImageField(upload_to="badge_templates/icons", null=True, blank=True)
    origin = models.CharField(max_length=128, null=True, blank=True, help_text=_("Badge template type."))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save()
        # auto-evaluate type:
        if not self.origin:
            self.origin = self.TYPE
            self.save(*args, **kwargs)
