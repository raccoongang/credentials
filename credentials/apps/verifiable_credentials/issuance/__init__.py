import json
import logging

import didkit
from asgiref.sync import async_to_sync
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer

from ..settings import vc_settings
from .models import IssuanceLine


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

    def __init__(self, *, request_data, issuance_uuid):
        self._issuance_line = self._pickup_issuance_line(issuance_uuid)
        self._storage = self._issuance_line.storage
        self._validate(request_data)

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

    def _validate(self, request_data):
        """
        Check incoming request data and update issuance line if needed.
        """
        serializer = self._storage.get_request_serializer(self._issuance_line, data=request_data, partial=True)
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
        # TODO: build status entry
        credential_data = self._issuance_line.construct()
        return self._render(credential_data)

    def sign(self, composed_credential_json):
        """
        Sign the composed digital credential document.
        """
        didkit_options = {}
        verifiable_credential = sign_with_didkit(
            composed_credential_json, json.dumps(didkit_options), vc_settings.DEFAULT_ISSUER_KEY
        )
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
    def init(cls, *, user_credential, storage_id):
        """
        The very first action in verifiable credential issuance line.
        """
        issuance_line, __ = IssuanceLine.objects.get_or_create(
            user_credential=user_credential,
            storage_id=storage_id,
            processed=False,
            defaults={
                "issuer_id": IssuanceLine.resolve_issuer(),
                "data_model_id": IssuanceLine.resolve_data_model(storage_id).ID,
            },
        )
        return issuance_line


class JSONLDRenderer(JSONRenderer):
    """
    Renderer which serializes to JSON.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a string.

        Addionally, updates `data` shape a bit to conform json-ld specs.
        """

        tweaked_data = self._tweak(data)
        return super().render(tweaked_data, accepted_media_type, renderer_context).decode("utf-8")

    def _tweak(self, data):
        """
        Shape `data` with JSON-LD specifics.
        """
        data["@context"] = data.pop("context")
        return data


@async_to_sync
async def sign_with_didkit(credential, options, issuer_key):
    return await didkit.issue_credential(credential, options, issuer_key)  # pylint: disable=no-member
