"""
Badges DB models.
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from credentials.apps.credentials.models import AbstractCredential, UserCredential


class BadgeTemplate(AbstractCredential):
    """
    Describes badge credential type.
    """

    ORIGIN = "openedx"

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
            self.origin = self.ORIGIN
            self.save(*args, **kwargs)


class BadgeRequirement(models.Model):
    """
    Describes what must happen and its effect for badge template.

    NOTE: all requirement for a single badge template follow "AND" processing logic by default.
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

    NOTE: all data rules for a single requirement follow "AND" processing logic.
    """

    OPERATORS = Choices(
        ("eq", "="),
        # ('lt', '<'),
        # ('gt', '>'),
    )

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
        verbose_name=_("key path"),
    )
    operator = models.CharField(
        max_length=32,
        choices=OPERATORS,
        default=OPERATORS.eq,
        help_text=_(
            "Expected value comparison operator. https://docs.python.org/3/library/operator.html"
        ),
        verbose_name=_("action"),
    )
    value = models.CharField(
        max_length=255,
        help_text=_('Expected value for the nested property, e.g: "cucumber1997".'),
        verbose_name=_("expected value"),
    )


class BadgeProgress(models.Model):
    """
    Tracks a single badge template progress for user.
    """

    credential = models.OneToOneField(
        UserCredential,
        models.SET_NULL,
        blank=True,
        null=True,
    )
    username = models.CharField(max_length=255)  # index
    template = models.ForeignKey(
        BadgeTemplate,
        models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = _("badge progress records")

    def __str__(self):
        return f"BadgeProgress:{self.username}"


class Fulfillment(models.Model):
    """
    Completed badge template requirement for user.
    """

    progress = models.ForeignKey(BadgeProgress, on_delete=models.CASCADE)
    requirement = models.ForeignKey(
        BadgeRequirement,
        models.SET_NULL,
        blank=True,
        null=True,
    )
