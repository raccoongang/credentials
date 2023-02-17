import logging

from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from credentials.apps.credentials.models import UserCredential

from .models import IssuanceLine
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

    # compose_functions = {
    #     VERIFIABLE_CREDENTIAL_KEY: compose_verifiable_credential,
    #     OPEN_BADGES_V3_KEY: compose_open_badge_v3,
    # }

    def __init__(self, request_data, issuance_uuid):
        self._issuance_line = self._pickup_issuance_line(issuance_uuid)
        self._validated_data = self._validate(request_data)

    def _pickup_issuance_line(self, issuance_uuid):
        issuance_line = IssuanceLine.objects.filter(uuid=issuance_uuid).first()
        if not issuance_line:
            msg = _(f"Couldn't find such issuance line: ['issuance_uuid']")
            logger.exception(msg)
            raise ValidationError({'issuance_uuid': msg})

        return issuance_line

    def _validate(self, request_data):
        serializer = self._issuance_line.storage.ISSUANCE_REQUEST_SERIALIZER(data=request_data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @classmethod
    def init(cls, *, credential_uuid, storage_id):
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
        Compose a digital credential document for signing.
        """
        return self._validated_data

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


class IssuanceRequestSerializer(serializers.Serializer):
    """
    Incoming issuance request default serializer.

    It is expected incoming requests from different storages to have unified shape.
    But once it is not the case, swapping this class for something more specific is possible.
    """
    class Meta:
        fields = "__all__"

    holder = serializers.CharField(help_text=_("Learner DID"))
