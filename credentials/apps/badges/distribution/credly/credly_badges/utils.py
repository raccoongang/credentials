from django.shortcuts import get_object_or_404

from .rest_api import CredlyAPIClient
from .models import CredlyOrganization, BadgeTemplate


def sync_badge_templates_for_organization(organization_id):
    """
    Sync badge templates for a specific organization and create records in the database.

    Args:
        organization_id (str): UUID of the organization.

    Raises:
        Http404: If organization is not found.
    """
    organization = get_object_or_404(CredlyOrganization, uuid=organization_id)

    credly_api_client = CredlyAPIClient(organization_id, organization.api_key)
    badge_templates_data = credly_api_client.fetch_badge_templates()

    for badge_template_data in badge_templates_data.get('data', []):
        BadgeTemplate.objects.update_or_create(
            uuid=badge_template_data.get('id'),
            defaults={
                'name': badge_template_data.get('name'),
                'organization': organization,
            }
        )
