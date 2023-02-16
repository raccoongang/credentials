from credentials.apps.credentials.models import UserCredential

from .composition import compose_open_badge_v3, compose_verifiable_credential
from .constants import OPEN_BADGES_V3_KEY, VERIFIABLE_CREDENTIAL_KEY
from .models import VerifiableCredentialIssuance
from .settings import vc_settings


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
        self._issuance = VerifiableCredentialIssuance.objects.get(uuid=issuance_uuid)
        self._validated_data = self._validate(request_data)

    def _validate(storage_data):


    def serialize_request(self):
        """
        Serialize and validate the request data.
        """
        # TODO: Do we need this serialization?
        # serializer = IssuanceRequestSerializer(data=self.request_data)
        # if not serializer.is_valid():
        #     raise ValueError("Invalid request data")
        # return serializer.validated_data
        return self.request_data

    def compose(self):
        """
        Compose a digital credential document for signing.
        """
        validated_data = self.serialize_request()
        return self._get_compose_function()(data=validated_data)

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

        self.issuance.processed = True
        self.issuance.save()

        return verifiable_credential

    def _get_compose_function(self):
        """
        Choose an appropriate compose function.
        """
        return self.compose_functions[vc_settings.DEFAULT_DATA_MODEL]

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

    @classmethod
    def create_issuance_request(cls, credential_uuid):
        """
        Creates issuance request.
        Arguments:
            credential_uuid(str): Credential uuid.
        Returns
            str: UUID of issuance.
        """
        user_credential = UserCredential.objects.get(uuid=credential_uuid)

        return VerifiableCredentialIssuance.objects.create(
            user_credential=user_credential,
            issuer_did=vc_settings.DEFAULT_ISSUER_DID,
        )


class Issuance