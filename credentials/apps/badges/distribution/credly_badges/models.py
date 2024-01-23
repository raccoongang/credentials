"""
Credly badges DB models.
"""

from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class CredlyOrganization(TimeStampedModel):
    """
    A single Credly organization.
    """
    uuid = models.UUIDField(unique=True, help_text=_('Unique credly organization ID.'))
    name = models.CharField(max_length=255, help_text=_('Name of credly organization.'))
    api_key = models.CharField(max_length=255, help_text=_('Credly organization API bearer secret.'))
