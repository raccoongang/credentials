"""verifiable_credentials API v1 views."""
import logging

from django.contrib.auth import get_user_model
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from credentials.apps.verifiable_credentials.utils import get_user_program_certificates_data

from .serializers import ProgramCertificateSerializer


User = get_user_model()
log = logging.getLogger(__name__)


class ProgramCertificatesViewSet(viewsets.ViewSet):

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
    )

    permission_classes = ()

    def list(self, request, *args, **kwargs):
        """
        List data for all the user's issued program certificates.
        GET: /verifiable_credentials/api/v1/program_certificates/

        Arguments:
            request: A request to control data returned in endpoint response

        Returns:
            response(dict): Information about the user's program certificates
        """
        # TODO: check naming. Do I get `program certificate` data or `program credential` data?
        # TODO: request.user works improperly, why edx?
        program_certificates = get_user_program_certificates_data(request.user.username)

        serializer = ProgramCertificateSerializer(program_certificates, many=True)
        return Response({"program_certificates": serializer.data})
