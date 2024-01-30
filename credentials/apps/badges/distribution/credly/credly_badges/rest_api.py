import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_client import CredlyAPIClient
from .data import CredlyEventInfoData
from .models import CredlyOrganization
from .utils import (
    handle_badge_template_changed_event,
    handle_badge_template_created_event,
    handle_badge_template_deleted_event,
)


logger = logging.getLogger(__name__)


class CredlyWebhook(APIView):
    """
    Public API that handle Credly webhooks.

    Usage:
        POST /edx_badges/api/credly/v1/webhook
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        event_info_data = CredlyEventInfoData(**request.data)
        organization = get_object_or_404(CredlyOrganization, uuid=event_info_data.organization_id)
        credly_api_client = CredlyAPIClient(organization.uuid, organization.api_key)

        event_info_response = credly_api_client.fetch_event_information(event_info_data.id)

        if event_info_data.event_type == "badge_template.created":
            handle_badge_template_created_event(event_info_response)
        elif event_info_data.event_type == "badge_template.changed":
            handle_badge_template_changed_event(event_info_response)
        elif event_info_data.event_type == "badge_template.deleted":
            handle_badge_template_deleted_event(event_info_response)
        else:
            logger.error(f"Unknown event type: {event_info_data.event_type}")

        return Response(status=status.HTTP_204_NO_CONTENT)
