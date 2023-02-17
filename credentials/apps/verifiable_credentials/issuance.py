import logging
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from credentials.apps.credentials.models import UserCredential

from .settings import vc_settings

logger = logging.getLogger(__name__)


class CredentialIssuer:
    """
    Instances of this class manage the whole pipeline of verifiable credential issuance.

    Args:
        request_data: issuance HTTP API request
        issuance_uuid: (optional) identifier for current issuance line

    Steps:
        - incoming data validation
        - resolving issuance configuration
        - resolving data model to use for verifiable credential composition
        - composed verifiable credential signing
    """

    def __init__(self, request_data, issuance_uuid):
        self._issuance_line = self._pickup_issuance_line(issuance_uuid)
        self._validate(request_data)

    def _pickup_issuance_line(self, issuance_uuid):
        issuance_line = IssuanceLine.objects.filter(uuid=issuance_uuid).first()
        if not issuance_line:
            msg = _(f"Couldn't find such issuance line: ['issuance_uuid']")
            logger.exception(msg)
            raise ValidationError({'issuance_uuid': msg})

        return issuance_line

    def _validate(self, request_data):
        serializer = self._issuance_line.storage.ISSUANCE_REQUEST_SERIALIZER(self._issuance_line, data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    @classmethod
    def init(cls, *, credential_uuid, storage_id):
        """
        The very first action in verifiable credential issuance line.
        """
        user_credential = UserCredential.objects.filter(uuid=credential_uuid).first()
        # validate given user credential exists:
        if not user_credential:
            msg = _(f"No such user credential [{credential_uuid}]")
            logger.exception(msg)
            raise ValidationError({"credential_uuid": msg})

        # validate given storage is active:
        if not any(filter(lambda storage: storage.ID == storage_id, vc_settings.storages)):
            msg = _(f"Provided storage backend isn't active [{storage_id}]")
            logger.exception(msg)
            raise ValidationError({"storage_id": msg})

        # create init issuance line:
        issuance_line, _ = IssuanceLine.objects.get_or_create(
            user_credential=user_credential,
            issuer_id=credential_uuid,
            storage_id=storage_id,
        )
        return issuance_line

    def compose(self):
        """
        Construct an appropriate verifiable credential for signing.
        """
        return self._issuance_line.data_model

    def sign(self, composed_credential):
        """
        Sign the composed digital credential document.
        """
        signed_credential = composed_credential.copy()
        signed_credential["proof"] = {}
        return signed_credential

    def issue(self):
        """
        Issue a signed digital credential document by validating, composing, and signing.
        """
        composed_credential = self.compose()
        verifiable_credential = self.sign(composed_credential)

        self._issuance_line.processed = True
        self._issuance_line.save()

        return verifiable_credential

    def _get_issuance_config(self):
        """
        Load appropriate issuance configuration.
        """
        # TODO
        # use Org/Site or system defaults
        # add DID to Org/Site config
        # add key to Org/Site config

    def _load_keys(self):
        """
        Pick signing key(s).
        """
        pass


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
    holder_id = models.CharField(max_length=255, help_text=_("Holder DID"))
    subject_id = models.CharField(max_length=255, blank=True, null=True, help_text=_("Subject DID (if not provided corresponds to \"Holder ID\")"))

    def __str__(self) -> str:
        return f"IssuanceLine(user_credential={self.user_credential}, issuer_id={self.issuer_id}, storage_id={self.storage_id})"

    @property
    def storage(self):
        for storage in vc_settings.storages:
            if storage.ID == self.storage_id:
                return storage

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
            return vc_settings.FORCE_DATA_MODEL(self).data

        return self.storage.PREFERRED_DATA_MODEL(self).data


class IssuanceLineSerializer(serializers.ModelSerializer):
    """
    Incoming issuance request default serializer.

    It is expected incoming requests from different storages to have unified shape.
    But once it is not the case, swapping this class for something more specific is possible.
    """
    class Meta:
        model = IssuanceLine
        fields = "__all__"
        read_only_fields = ['uuid', 'user_credential', 'processed', 'issuer_id', 'storage_id']

    @staticmethod
    def swap_value(data: dict, source_key: str, target_key: str) -> None:
        data[target_key] = data.pop(source_key)
