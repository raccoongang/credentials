"""
Verifiable Credentials DB models.
"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from credentials.apps.credentials.models import UserCredential

from .settings import vc_settings
from .utils import get_storage


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
    data_model = models.CharField(max_length=255, blank=True, null=True, help_text=_("Data model lookup"))
    expiration_date = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self) -> str:
        return (
            f"IssuanceLine(user_credential={self.user_credential}, "
            f"issuer_id={self.issuer_id}, storage_id={self.storage_id})"
        )

    @property
    def storage(self):
        return get_storage(self.storage_id)

    @classmethod
    def get_data_model(cls, storage_id):
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

        return get_storage(storage_id).PREFERRED_DATA_MODEL

    def construct(self):
        serializer = self.get_data_model(self.storage_id)(self)
        return serializer.data

    def mark_processed(self):
        self.processed = True
        self.save()
