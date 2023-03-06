"""
Verifiable Credentials DB models.
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

    # Initial data:
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
    # Storage request data:
    holder_id = models.CharField(max_length=255, blank=True, null=True, help_text=_("Holder DID"))
    subject_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Subject DID (if not provided corresponds to "Holder ID")'),
    )

    def __str__(self) -> str:
        return (
            f"IssuanceLine(user_credential={self.user_credential}, "
            f"issuer_id={self.issuer_id}, storage_id={self.storage_id})"
        )

    @property
    def storage(self):
        for storage in vc_settings.DEFAULT_STORAGES:
            if storage.ID == self.storage_id:
                return storage
        return None

    @property
    def data_model(self):
        """
        Data model lookup:
        - check if there is FORCE_DATA_MODEL set
        - check issuance request options (not implemented)
        - check current storage preference
        - use default
        """
        # Pin data model choice no matter what:
        if vc_settings.FORCE_DATA_MODEL is not None:
            return vc_settings.FORCE_DATA_MODEL

        return self.storage.PREFERRED_DATA_MODEL

    def construct(self):
        serializer = self.data_model(self)
        return serializer.data

    def mark_processed(self):
        self.processed = True
        self.save()
