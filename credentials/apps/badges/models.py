"""
Badges DB models.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from credentials.apps.core.utils import _choices
from credentials.apps.credentials.models import AbstractCredential

from .constants import BadgeTemplateStatus


class BadgeTemplate(AbstractCredential):
    """
    Describes badge credential type.
    """

    uuid = models.UUIDField(unique=True, help_text=_("Unique badge template ID."))
    name = models.CharField(max_length=255, help_text=_("Badge template name."))
    type = models.CharField(max_length=255, default="openedx")
    status = models.CharField(
        max_length=255,
        choices=_choices(
            BadgeTemplateStatus.ACTIVE,
            BadgeTemplateStatus.ARCHIVED,
            BadgeTemplateStatus.DRAFT,
            BadgeTemplateStatus.REVOKED,
        ),
        help_text=_("Status of the badge template."),
    )
    description = models.TextField(null=True, blank=True, help_text=_("Badge template description."))
    icon = models.ImageField(upload_to="badge_templates/icons", null=True, blank=True)

    def __str__(self):
        return self.name
