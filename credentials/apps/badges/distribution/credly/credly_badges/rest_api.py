import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_client import CredlyAPIClient
from .models import CredlyOrganization
from .utils import (
    handle_badge_template_changed_event,
    handle_badge_template_created_event,
    handle_badge_template_deleted_event,
)


logger = logging.getLogger(__name__)


class CredlyWebhook(APIView):
    """
    Public API (webhook endpoint) to handle incoming Credly updates.

    Usage:
        POST <credentials>/credly-badges/api/webhook/
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Handle incoming update events from the Credly service.

        https://sandbox.credly.com/docs/webhooks#requirements

        Handled events:
            - badge_template.created
            - badge_template.changed
            - badge_template.deleted

        - tries to recognize Credly Organization context;
        - validates event type and its payload;
        - performs corresponding item (badge template) updates;

        Returned statuses:
            - 204
            - 404
        """
        organization = get_object_or_404(CredlyOrganization, uuid=request.data.get("organization_id"))
        credly_api_client = CredlyAPIClient(organization.uuid, organization.api_key)

        event_info_response = credly_api_client.fetch_event_information(request.data.get("id"))
        event_type = request.data.get("event_type")

        if event_type == "badge_template.created":
            handle_badge_template_created_event(event_info_response)
        elif event_type == "badge_template.changed":
            handle_badge_template_changed_event(event_info_response)
        elif event_type == "badge_template.deleted":
            handle_badge_template_deleted_event(event_info_response)
        else:
            logger.error(f"Unknown event type: {event_type}")

        return Response(status=status.HTTP_204_NO_CONTENT)
