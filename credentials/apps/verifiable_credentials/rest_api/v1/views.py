"""verifiable_credentials API v1 views."""
from django.contrib.auth import get_user_model
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from credentials.apps.verifiable_credentials.issuance import CredentialIssuer
from credentials.apps.verifiable_credentials.settings import vc_settings
from credentials.apps.verifiable_credentials.utils import get_user_program_credentials_data

from .serializers import ProgramCredentialSerializer

User = get_user_model()


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
        program_credentials = get_user_program_credentials_data(
            request.user.username)

        serializer = ProgramCredentialSerializer(
            program_credentials, many=True)
        return Response({"program_credentials": serializer.data})


class QRCodeView(APIView):
    """
    Generates a QR code for VC issuance process initiation.
    POST: /verifiable_credentials/api/v1/qrcode/
    POST Parameters:
        * uuid: Required. An unique uuid for UserCredential
    Returns:
        response(dict): base64 encoded qrcode
    """

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
    )

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        credential_uuid = request.data.get("uuid")

        if not credential_uuid:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({"qrcode": "<base64-encoded-content>"})


class DeeplinkView(APIView):
    """
    Generates a deeplink for VC issuance process initiation.
    POST: /verifiable_credentials/api/v1/deeplink/
    POST Parameters:
        * uuid: Required. An unique uuid for UserCredential
    Returns:
        response(dict): parametrized deep link
    """

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
    )

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        credential_id = request.data.get("credential_id")
        storage_id = request.data.get("storage_id")

        if not all([credential_id, storage_id]):
            return Response("Incomplete required data", status=status.HTTP_400_BAD_REQUEST)

        issuance = CredentialIssuer.init(context={
            'credential_id': credential_id,
            'storage_id': storage_id,
        })

        return Response({"deeplink": Wallet.create_deeplink_url(issuance.uuid)})


class IssueCredentialView(APIView):
    """
    This API endpoint allow requests for VC issuing.
    POST: /verifiable_credentials/api/v1/credential/issue

    Request and response should conform VC API specs:
    https://w3c-ccg.github.io/vc-api/#issue-credential
    """

    authentication_classes = ()

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        credential_issuer = CredentialIssuer(request.data, kwargs.get("issuance_uuid"))
        return Response(
            {"verifiableCredential": credential_issuer.issue()},
            status=status.HTTP_201_CREATED
        )
