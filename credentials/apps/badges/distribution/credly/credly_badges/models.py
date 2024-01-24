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
