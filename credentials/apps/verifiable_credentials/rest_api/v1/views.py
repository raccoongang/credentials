"""verifiable_credentials API v1 views."""
from django.conf import settings
from django.contrib.auth import get_user_model
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
        program_credentials = get_user_program_credentials_data(request.user.username)

        serializer = ProgramCredentialSerializer(program_credentials, many=True)
        return Response({"program_credentials": serializer.data})


class VCIssuanceQRCodeView(APIView):
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


class VCIssuanceDeeplinkView(APIView):
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
        credential_uuid = request.data.get("uuid")

        if not credential_uuid:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({"deeplink": "<parametrized-deep-link>"})


class VCIssuanceWalletView(APIView):
    """
    This API endpoint allow requests for VC issuing.
    GET: /verifiable_credentials/api/v1/wallet/

    Arguments:
        request: A request to control data returned in endpoint response

    Returns:
        response(dict): signed VC document for storing
    """

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
    )

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({"document_format": settings.VC_DEFAULT_STANDARD})
