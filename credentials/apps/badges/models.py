"""
Badges DB models.
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from credentials.apps.credentials.models import AbstractCredential


class BadgeTemplate(AbstractCredential):
    """
    Describes badge credential type.
    """

    TYPE = "openedx"

    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text=_("Unique badge template ID.")
    )
    name = models.CharField(max_length=255, help_text=_("Badge template name."))
    description = models.TextField(
        null=True, blank=True, help_text=_("Badge template description.")
    )
    icon = models.ImageField(upload_to="badge_templates/icons", null=True, blank=True)
    origin = models.CharField(
        max_length=128, null=True, blank=True, help_text=_("Badge template type.")
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save()
        # auto-evaluate type:
        if not self.origin:
            self.origin = self.TYPE
            self.save(*args, **kwargs)


class BadgeRequirement(models.Model):
    """
    Describes what must happen and its effect for badge template.
    """

    EFFECTS = Choices("award", "revoke")

    template = models.ForeignKey(
        BadgeTemplate,
        on_delete=models.CASCADE,
        help_text=_("Badge template this requirement serves for."),
    )
    event_type = models.CharField(
        max_length=255,
        help_text=_(
            'Public signal type. Use namespaced types, e.g: "org.openedx.learning.student.registration.completed.v1"'
        ),
    )
    effect = models.CharField(
        max_length=32,
        choices=EFFECTS,
        default=EFFECTS.award,
        help_text=_("Defines how this requirement contributes to badge earning."),
    )
    description = models.TextField(
        null=True, blank=True, help_text=_("Provide more details if needed.")
    )

    def __str__(self):
        return f"BadgeRequirement:{self.id}:{self.template.uuid}"


class DataRule(models.Model):
    """
    Specifies expected data attribute value for event payload.
    """

    requirement = models.ForeignKey(
        BadgeRequirement,
        on_delete=models.CASCADE,
        help_text=_("Parent requirement for this data rule."),
    )
    path = models.CharField(
        max_length=255,
        help_text=_(
            'Public signal\'s data payload nested property path, e.g: "user.pii.username".'
        ),
    )
    value = models.CharField(
        max_length=255,
        help_text=_(
            'Expected value for the nested property, e.g: "cucumber1997".'
        ),
    )
