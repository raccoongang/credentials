"""
Issuance line processor.
"""
import json
import logging

import didkit
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from ..issuance import IssuanceException, sign_with_didkit
from ..settings import vc_settings
from .models import IssuanceLine, get_issuer


logger = logging.getLogger(__name__)


class CredentialIssuer:
    """
    Instances of this class manage the whole pipeline of verifiable credential issuance.

    Args:
        data: issuance HTTP API request
        issuance_uuid: (optional) identifier for current issuance line

    Steps:
        - incoming data validation
        - resolving issuance configuration
        - resolving data model to use for verifiable credential composition
        - composed verifiable credential signing
    """

    def __init__(self, *, data, issuance_uuid):
        self._issuance_line = self._pickup_issuance_line(issuance_uuid)
        self._storage = self._issuance_line.storage
        self._validate(data)

    def _pickup_issuance_line(self, issuance_uuid):
        """
        Find previously initiated issuance line for processing.
        """
        issuance_line = IssuanceLine.objects.filter(uuid=issuance_uuid).first()
        if not issuance_line:
            msg = _("Couldn't find such issuance line: [{issuance_uuid}]").format(issuance_uuid=issuance_uuid)
            logger.exception(msg)
            raise ValidationError({"issuance_uuid": msg})

        return issuance_line

    def _validate(self, initial_data):
        """
        Check incoming request data and update issuance line if needed.
        """
        serializer = self._storage.get_request_serializer(self._issuance_line, data=initial_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def _render(self, data):
        """
        Shape raw data.
        """
        return vc_settings.DEFAULT_RENDERER().render(data)

    def compose(self):
        """
        Construct an appropriate verifiable credential for signing.
        """
        # FIXME: build status entry
        credential_data = self._issuance_line.construct()
        return self._render(credential_data)

    def sign(self, composed_credential_json):
        """
        Sign the composed digital credential document.
        """
        err_message = _("Provided data didn't validate")
        err_detail = ""

        didkit_options = {}
        issuer_key = get_issuer(self._issuance_line.issuer_id).issuer_key

        try:
            verifiable_credential = sign_with_didkit(composed_credential_json, json.dumps(didkit_options), issuer_key)
        except didkit.DIDKitException as exc:  # pylint: disable=no-member
            logger.exception(err_message)
            if "expansion failed" in str(exc):
                err_detail = _("defined property wasn't found within the linked data graph")
            raise IssuanceException(detail=f"{err_message} [{err_detail}]")
        except ValueError:
            err_detail = _("identifier not recognized")
            raise IssuanceException(detail=f"{err_message} [{err_detail}]")

        verifiable_credential = json.loads(verifiable_credential)
        return verifiable_credential

    def issue(self):
        """
        Issue a signed digital credential document by validating, composing, and signing.
        """
        # construction (data collecting and shaping):
        composed_credential = self.compose()

        # signing / structure validation:
        verifiable_credential = self.sign(composed_credential)

        # issuance line finalization:
        self._issuance_line.mark_processed()

        return verifiable_credential

    @classmethod
    def init(cls, *, storage_id, user_credential=None, issuer_id=None):
        """
        The very first action in verifiable credential issuance line.

        NOTE: User credential is not provided for status list special case issuance.
        """

        data_model_id = IssuanceLine.resolve_data_model(storage_id).ID
        status = getattr(user_credential, "status", None)
        status_index = IssuanceLine.get_next_status_index(issuer_id)

        if issuer_id is None:
            issuer_id = IssuanceLine.resolve_issuer()

        # special case - Status List isn't related to any specific achievement:
        if user_credential is None:
            status_index = None

        issuance_line, __ = IssuanceLine.objects.get_or_create(
            user_credential=user_credential,
            storage_id=storage_id,
            processed=False,
            defaults={
                "issuer_id": issuer_id,
                "data_model_id": data_model_id,
                "status_index": status_index,
                "status": status,
            },
        )
        return issuance_line
