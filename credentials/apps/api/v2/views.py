"""
Credentials service API views (v1).
"""
import logging

from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError

from credentials.apps.api.filters import ProgramFilterByUuid
from credentials.apps.api.serializers import UserCredentialSerializer
from credentials.apps.credentials.models import UserCredential


log = logging.getLogger(__name__)


class ProgramsCredentialsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """It will return the all credentials for programs based on the program_uuid."""
    queryset = UserCredential.objects.all()
    filter_class = ProgramFilterByUuid
    serializer_class = UserCredentialSerializer

    def list(self, request, *args, **kwargs):
        # Validate that we do have a program_uuid to use
        if not self.request.query_params.get('program_uuid'):
            raise ValidationError(
                {'error': 'A UUID query string parameter is required for filtering program credentials.'})

        # Confirmation that we are not supplying both parameters. We should only be providing the program_uuid in V2
        if self.request.query_params.get('program_id'):
            raise ValidationError(
                {'error': 'A program_id query string parameter was found in a V2 API request.'})

        # pylint: disable=maybe-no-member
        return super(ProgramsCredentialsViewSet, self).list(request, *args, **kwargs)
