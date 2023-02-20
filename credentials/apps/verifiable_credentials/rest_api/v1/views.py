"""
Verifiable Credentials API v1 views.
"""
import logging

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render

from credentials.apps.verifiable_credentials.issuance import CredentialIssuer
from credentials.apps.verifiable_credentials.utils import (
    generate_base64_qr_code,
    get_user_program_credentials_data,
    is_valid_uuid,
)

from .serializers import ProgramCredentialSerializer

logger = logging.getLogger(__name__)

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


class InitIssuanceView(APIView):
    """
    Generates a deeplink, qrcode for VC issuance process initiation.

    POST: /verifiable_credentials/api/v1/credentials/init

    POST Parameters:
        * credential_id: Required. An unique UserCredential identifier.
        * storage_id: Required. Requested storage (wallet) identifier.
    Returns:
        response(dict): parametrized deep link, qrcode and mobile app links
    """

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
    )

    # permission_classes = (IsAuthenticated,)
    permission_classes = ()

    def post(self, request):
        credential_uuid = request.data.get("credential_uuid")
        storage_id = request.data.get("storage_id")

        if not all([credential_uuid, storage_id]):
            msg = _(f"Incomplete required data: ['credential_uuid', 'storage_id']")
            logger.exception(msg)
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        if not is_valid_uuid(credential_uuid):
            msg = _(f"Credential identifier must be valid UUID: ['credential_uuid']")
            logger.exception(msg)
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        issuance_line = CredentialIssuer.init(
            credential_uuid=credential_uuid,
            storage_id=storage_id,
        )

        deeplink = issuance_line.storage.get_deeplink_url(issuance_line.uuid)

        init_data = {
            "deeplink": deeplink,
            "qrcode": generate_base64_qr_code(deeplink),
        }

        if issuance_line.storage.is_mobile():
            init_data.update(
                {
                    "app_link_android": issuance_line.storage.APP_LINK_ANDROID,
                    "app_link_ios": issuance_line.storage.APP_LINK_IOS,
                }
            )

        return Response(init_data)


class IssueCredentialView(APIView):
    """
    This API endpoint allows requests for VC issuing.

    POST: /verifiable_credentials/api/v1/credential/issue

    Request and response should conform VC API specs:
    https://w3c-ccg.github.io/vc-api/#issue-credential
    """

    authentication_classes = ()

    # permission_classes = (IsAuthenticated,)
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        credential_issuer = CredentialIssuer(request.data, kwargs.get("issuance_line_uuid"))

        return Response({"verifiableCredential": credential_issuer.issue()}, status=status.HTTP_201_CREATED)


class NoWalletView(APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        return render(
            request,
            "verifiable_credentials/no-wallet.html",
            context={"title": _("Verifiable Credentials issuance sandbox"), "content": request.query_params},
        )
