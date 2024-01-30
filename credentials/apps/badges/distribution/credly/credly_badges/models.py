"""
Credly Badges DB models.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel


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


class BadgeTemplate(models.Model):
    """
    Badge template model.
    """
    STATE_CHOICES = (
        ('active', _('Active')),
        ('archived', _('Archived')),
        ('draft', _('Draft')),
        ('inactive', _('Inactive')),
    )

    uuid = models.UUIDField(unique=True, help_text=_('Unique badge template ID.'))
    name = models.CharField(max_length=255, help_text=_('Badge template name.'))
    organization = models.ForeignKey(
        CredlyOrganization,
        on_delete=models.CASCADE,
        help_text=_('Organization of the badge template.')
    )
    state = models.CharField(
        max_length=255,
        choices=STATE_CHOICES,
        default='inactive',
        help_text=_('State of the badge template.')
    )

    def __str__(self):
        return self.name
