"""
Database models for verifiable_credentials.
"""
from config_models.models import ConfigurationModel
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from credentials.apps.catalog.models import Organization

from .constants import OPEN_BADGES_V3_KEY, VERIFIABLE_CREDENTIAL_KEY


class IssuanceConfiguration(ConfigurationModel):
    """
    A model representing the configuration settings for digital credentials issuance.
    This model stores the details needed to generate and issue digital credentials,
    such as credential format, site, etc.

    .. no_pii:
    """

    KEY_FIELDS = (
        "site_id",
        "slug",
    )
    DIGITAL_CREDENTIAL_FORMAT_CHOICES = (
        (VERIFIABLE_CREDENTIAL_KEY, _("Verifiable Credentials")),
        (OPEN_BADGES_V3_KEY, _("Open Badges v3")),
    )

    enabled = models.BooleanField(default=False)
    site = models.ForeignKey(
        Site,
        default=settings.SITE_ID,
        related_name="%(class)ss",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(
        max_length=30,
        default="default",
        blank=True,
    )
    organization = models.ForeignKey(
        Organization,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    digital_credential_format = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_("Digital Credential Format"),
        default=VERIFIABLE_CREDENTIAL_KEY,
        choices=DIGITAL_CREDENTIAL_FORMAT_CHOICES,
    )
