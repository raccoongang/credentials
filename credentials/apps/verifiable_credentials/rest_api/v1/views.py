"""verifiable_credentials API v1 views."""
from django.contrib.auth import get_user_model
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from credentials.apps.verifiable_credentials.utils import get_user_program_credentials_data

from .serializers import ProgramCredentialSerializer


User = get_user_model()


class ProgramCredentialsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    # FIXME: for some reasons authentication not working
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
