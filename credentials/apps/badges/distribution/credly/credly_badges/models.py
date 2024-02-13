"""
Credly Badges DB models.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from model_utils.fields import StatusField

from credentials.apps.badges.models import BadgeTemplate


class CredlyOrganization(TimeStampedModel):
    """
    Credly Organization configuration.
    """

    uuid = models.UUIDField(unique=True, help_text=_("Put your Credly Organization ID here."))
    api_key = models.CharField(max_length=255, help_text=_("Credly API shared secret for Credly Organization."))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Verbose name for Credly Organization."))

    def __str__(self):
        return f"{self.name or self.uuid}"

    @classmethod
    def get_all_organization_ids(cls):
        """
        Get all organization IDs.
        """
        return cls.objects.values_list("uuid", flat=True)


class CredlyBadgeTemplate(BadgeTemplate):
    """
    Credly badge template.
    """

    TYPE = "credly"
    STATE = Choices("draft", "active", "archived")

    organization = models.ForeignKey(
        CredlyOrganization,
        on_delete=models.CASCADE,
        help_text=_("Credly Organization - template owner."),
    )
    state = StatusField(
        choices_name="STATE",
        help_text=_("Credly badge template state (auto-managed)."),
    )
