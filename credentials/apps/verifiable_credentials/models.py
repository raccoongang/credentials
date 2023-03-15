"""
Verifiable Credentials DB models.
"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from credentials.apps.credentials.models import UserCredential

from .composition import get_available_data_models, get_data_model
from .settings import vc_settings
from .storages import get_storage


def generate_data_model_choices():
    return [(data_model.ID, data_model.NAME) for data_model in get_available_data_models()]


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
    subject_id = models.CharField(
        max_length=255,
        help_text=_("Verifiable credential subject DID"),
    )
    data_model_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Verifiable credential specification to use"),
        choices=generate_data_model_choices(),
    )
    expiration_date = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self) -> str:
        return (
            f"IssuanceLine(user_credential={self.user_credential}, "
            f"issuer_id={self.issuer_id}, storage_id={self.storage_id})"
        )

    @property
    def storage(self):
        return get_storage(self.storage_id)

    @property
    def data_model(self):
        return get_data_model(self.data_model_id)

    def construct(self):
        serializer = self.data_model(self)
        return serializer.data

    def mark_processed(self):
        self.processed = True
        self.save()

    @classmethod
    def resolve_issuer(cls):
        """
        Unconditionally (for now) returns system-level Issier ID.
        """
        return vc_settings.DEFAULT_ISSUER_DID

    @classmethod
    def resolve_data_model(cls, storage_id):
        """
        Data model lookup:
        - check if there is FORCE_DATA_MODEL set
        - check current storage preference
        - or use the first one from the available ones
        """
        # Pin data model choice no matter what:
        if vc_settings.FORCE_DATA_MODEL is not None:
            return vc_settings.FORCE_DATA_MODEL

        return get_storage(storage_id).PREFERRED_DATA_MODEL
