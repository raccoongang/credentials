"""
Verifiable Credentials DB models.
"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from credentials.apps.credentials.models import UserCredential

from ..composition import get_available_data_models, get_data_model
from ..settings import vc_settings
from ..storages import get_storage


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
        null=True,
        blank=True,
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
    status_index = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Defines a position in the Status List sequence"),
    )
    status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Keeps track on a corresponding user credential's status"),
    )

    def __str__(self):
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

    @property
    def issuer_name(self):
        return getattr(get_issuer(self.issuer_id), "name", None)

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
        return get_default_issuer()

    @classmethod
    def resolve_data_model(cls, storage_id):
        """
        Data model lookup:
        - check current storage preference
        - or use the first one from the available ones
        """
        return get_storage(storage_id).PREFERRED_DATA_MODEL

    @classmethod
    def get_next_status_index(cls, issuer_id):
        """
        Return next status list position for given Issuer.
        """
        last = cls.objects.filter(issuer_id=issuer_id, status_index__gte=0).last()
        if not last:
            return 0
        return last.status_index + 1

    @classmethod
    def get_indicies_for_status(cls, *, issuer_id, status):
        """
        Status indicies with revoked credentials for given Issuer.
        """
        return list(
            cls.objects.filter(
                issuer_id=issuer_id,
                user_credential__status=status,
                processed=True,
                status_index__gte=0,
            )
            .order_by("status_index")
            .values_list("status_index", flat=True)
        )


class IssuanceConfiguration(TimeStampedModel):
    """
    Verifiable credentials issuer configuration.

    The model stores a details needed to compose and issue verifiable credentials.

    .. no_pii:

    NOTE:
        - current issuer by default has a system-wide scope;
        - it is expected an explicit `scope` ("system"|"site"|"org"|"course") field will be used in the future;
        - additional issuer preferences may live here as well (credential claims, storages filtering, etc.);
    """

    enabled = models.BooleanField(default=False)
    issuer_id = models.CharField(primary_key=True, max_length=255, help_text=_("Issuer DID"))
    issuer_key = models.JSONField(
        help_text=_("Issuer secret key. See: https://w3c-ccg.github.io/did-method-key/#ed25519-x25519")
    )
    issuer_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["enabled"]

    @classmethod
    def create_issuers(cls):
        """
        Create issuance configuration(s) from deployment configuration.

        Top level scope issuer is the must (auto-created).
        """
        IssuanceConfiguration.objects.get_or_create(
            issuer_id=vc_settings.DEFAULT_ISSUER.get("ID"),
            issuer_key=vc_settings.DEFAULT_ISSUER.get("KEY"),
            defaults={
                "enabled": True,
                "issuer_name": vc_settings.DEFAULT_ISSUER.get("NAME"),
            },
        )


def create_issuers():
    """
    Initiate issuers.
    """
    IssuanceConfiguration.create_issuers()


def get_registered_issuers():
    """
    Collect all levels issuers.
    """
    # currently, the only (system level, default) is supported.
    return list(IssuanceConfiguration.objects.filter(enabled=True).values())


def get_default_issuer():
    """
    Fetch the default issuer.
    """
    issuer = IssuanceConfiguration.objects.filter(enable=True).first()
    if issuer:
        return issuer

    # NOTE: pick the first one if all are disabled for some reason.
    IssuanceConfiguration.objects.first()


def get_issuer(issuer_id):
    """
    Fetch issuer by given ID.
    """
    issuer = IssuanceConfiguration.objects.filter(issuer_id=issuer_id).first()
    return issuer


def get_revoked_indices(issuer_id):
    """
    Collect status indicies for verifiable credentials with revoked achievements (in given Issuer context).
    """
    return IssuanceLine.get_indicies_for_status(issuer_id=issuer_id, status=UserCredential.REVOKED)
