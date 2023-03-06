import json
import logging

from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from credentials.apps.credentials.models import UserCredential

from .models import IssuanceLine
from .settings import vc_settings
from .utils import sign_with_didkit


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
            msg = _("Couldn't find such issuance line: ['issuance_uuid']")
            logger.exception(msg)
            raise ValidationError({"issuance_uuid": msg})

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
            msg = _("No such user credential [%(credential_uuid)s]") % {"credential_uuid": credential_uuid}
            logger.exception(msg)
            raise ValidationError({"credential_uuid": msg})

        # validate given storage is active:
        if not any(filter(lambda storage: storage.ID == storage_id, vc_settings.DEFAULT_STORAGES)):
            msg = _("Provided storage backend isn't active [%(storage_id)s]") % {"storage_id": storage_id}
            logger.exception(msg)
            raise ValidationError({"storage_id": msg})

        # create init issuance line:
        issuance_line, __ = IssuanceLine.objects.get_or_create(
            user_credential=user_credential,
            issuer_id=vc_settings.DEFAULT_ISSUER_DID,
            storage_id=storage_id,
        )
        return issuance_line

    def compose(self):
        """
        Construct an appropriate verifiable credential for signing.
        """
        # TODO: build status entry
        return self._issuance_line.construct()

    def sign(self, composed_credential):
        """
        Sign the composed digital credential document.
        """
        didkit_options = {}
        verifiable_credential = sign_with_didkit(
            json.dumps(composed_credential), json.dumps(didkit_options), vc_settings.DEFAULT_ISSUER_KEY
        )
        verifiable_credential = json.loads(verifiable_credential)
        return verifiable_credential

    def issue(self):
        """
        Issue a signed digital credential document by validating, composing, and signing.
        """
        composed_credential = self.compose()
        verifiable_credential = self.sign(composed_credential)
        self._issuance_line.mark_processed()

        return verifiable_credential
