"""
Database models for verifiable_credentials.
"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from credentials.apps.credentials.models import UserCredential

from .settings import vc_settings


class IssuanceLine(TimeStampedModel):
    """
    Specific verifiable credential issuance details (issuance line).

    .. no_pii:
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_credential = models.ForeignKey(
        UserCredential,
        related_name="vc_issues",
        on_delete=models.PROTECT,
        help_text=_("Related Open edX learner credential"),
    )
    processed = models.BooleanField(default=False, help_text=_("Completeness indicator"))
    issuer_id = models.CharField(max_length=255, help_text=_("Issuer DID"))
    storage_id = models.CharField(max_length=128, help_text=_("Target storage identifier"))

    def __str__(self) -> str:
        return f"IssuanceLine(user_credential={self.user_credential}, issuer_id={self.issuer_id}, storage_id={self.storage_id})"

    @property
    def storage(self):
        for storage in vc_settings.storages:
            if storage.ID == self.storage_id:
                return storage
