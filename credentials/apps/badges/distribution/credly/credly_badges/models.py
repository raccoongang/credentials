"""
Credly Badges DB models.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from credentials.apps.badges.models import BadgeTemplate


class CredlyOrganization(TimeStampedModel):
    """
    Credly organization configuration.
    """
    uuid = models.UUIDField(unique=True, help_text=_('Unique organization ID.'))
    name = models.CharField(max_length=255, help_text=_('Organization display name.'))
    api_key = models.CharField(max_length=255, help_text=_('Credly API shared secret for organization.'))

    def __str__(self):
        return self.name

    @classmethod
    def get_all_organization_ids(cls):
        """
        Get all organization IDs.
        """
        return cls.objects.values_list('uuid', flat=True)


class CredlyBadgeTemplate(BadgeTemplate):
    """
    Credly badge template model.
    """

    organization = models.ForeignKey(
        CredlyOrganization,
        on_delete=models.CASCADE,
        help_text=_('Organization of the credly badge template.')
    )
