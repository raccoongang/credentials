import json
import logging

from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from .composition.status_list import StatusListDataModel
from .models import IssuanceLine, UserCredential
from .settings import VerifiableCredentialsImproperlyConfigured, vc_settings
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

    def _get_key(self):
        key = vc_settings.DEFAULT_ISSUER_KEY
        if key is None:
            msg = _("Issuer key must be provided!")
            raise VerifiableCredentialsImproperlyConfigured(msg)
        return key

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
        issuance_line, created = IssuanceLine.objects.get_or_create(
            user_credential=user_credential,
            issuer_id=credential_uuid,
            storage_id=storage_id,
            defaults={
                "status_index": IssuanceLine.get_next_status_index(),
            },
        )

        # generate status list
        if created:
            status_list = StatusListDataModel(data={"issuer": "did:example:abc"})
            status_list.is_valid()
            status_list.save()

        return issuance_line

    def compose(self):
        """
        Construct an appropriate verifiable credential for signing.
        """
        return self._issuance_line.construct()

    def sign(self, composed_credential):
        """
        Sign a credential document.
        """
        return composed_credential  # FIXME: remove this line

        didkit_options = {}

        verifiable_credential = sign_with_didkit(
            json.dumps(composed_credential),
            json.dumps(didkit_options),
            self._get_key()
        )

        return json.loads(verifiable_credential)

    def issue(self):
        """
        Issue a signed digital credential document by validating, composing, and signing.
        """
        # construct a digital credential from a given data model:
        composed_credential = self.compose()

        # add a proof:
        verifiable_credential = self.sign(composed_credential)

        # finalize issuance:
        self._issuance_line.mark_processed()

        return verifiable_credential
