"""verifiable_credentials API v1 views."""
from django.contrib.auth import get_user_model
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from credentials.apps.verifiable_credentials.issuance import CredentialIssuer
from credentials.apps.verifiable_credentials.settings import vc_settings
from credentials.apps.verifiable_credentials.utils import get_user_program_credentials_data

from .serializers import ProgramCredentialSerializer


User = get_user_model()
Wallet = vc_settings.DEFAULT_WALLET


class ProgramCredentialsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
    )

    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        """
        List data for all the user's issued program credentials.
        GET: /verifiable_credentials/api/v1/program_credentials/
        Arguments:
            request: A request to control data returned in endpoint response
        Returns:
            response(dict): Information about the user's program credentials
        """
        program_credentials = get_user_program_credentials_data(request.user.username)

        serializer = ProgramCredentialSerializer(program_credentials, many=True)
        return Response({"program_credentials": serializer.data})


class InitIssuanceView(APIView):
    """
    Generates a deeplink, qrcode for VC issuance process initiation.
    POST: /verifiable_credentials/api/v1/credentials/init
    POST Parameters:
        * uuid: Required. An unique uuid for UserCredential
    Returns:
        response(dict): parametrized deep link, qrcode and mobile app links
    """

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
    )

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        credential_uuid = request.data.get("uuid")

        if not credential_uuid:
            return Response("Credential uuid is required", status=status.HTTP_400_BAD_REQUEST)

        issuance = CredentialIssuer.create_issuance_request(credential_uuid)

        return Response(
            {
                "deeplink": Wallet.create_deeplink_url(issuance.uuid),
                "qrcode": Wallet.create_qr_code(issuance.uuid),
                "app_link_android": Wallet.APP_LINK_ANDROID,
                "app_link_ios": Wallet.APP_LINK_IOS,
            }
        )


class IssueCredentialView(APIView):
    """
    This API endpoint allow requests for VC issuing.
    POST: /verifiable_credentials/api/v1/credential/issue/{issuance_uuid}
    Arguments:
        request: A request to control data returned in endpoint response
    Returns:
        response(dict): signed VC document for storing
    """

    authentication_classes = ()

    permission_classes = ()

    def post(self, request, *args, **kwargs):
        credential_issuer = CredentialIssuer(request.data, kwargs.get("issuance_uuid"))
        verifiable_credential_document = credential_issuer.issue()

        return Response(verifiable_credential_document)
