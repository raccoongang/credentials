from django.shortcuts import get_object_or_404
from crum import get_current_request

from .api_client import CredlyAPIClient
from .models import CredlyBadgeTemplate, CredlyOrganization


def sync_badge_templates_for_organization(organization_id):
    """
    Sync badge templates for a specific organization and create records in the database.

    Args:
        organization_id (str): UUID of the organization.

    Raises:
        Http404: If organization is not found.

    TODO: define and delete badge templates which was deleted on credly but still exists in our database
    """
    organization = get_object_or_404(CredlyOrganization, uuid=organization_id)

    credly_api_client = CredlyAPIClient(organization_id, organization.api_key)
    badge_templates_data = credly_api_client.fetch_badge_templates()

    for badge_template_data in badge_templates_data.get('data', []):
        CredlyBadgeTemplate.objects.update_or_create(
            uuid=badge_template_data.get('id'),
            defaults={
                'name': badge_template_data.get('name'),
                'organization': organization,
                'status': badge_template_data.get('state'),
                'site': get_current_request().site,
                'type': 'credly',
            }
        )


def handle_badge_template_created_event(data):
    """
    Create a new badge template.
    """
    badge_template = data.get('data', {}).get('badge_template', {})
    owner = data.get('data', {}).get('badge_template', {}).get('owner', {})

    organization = get_object_or_404(CredlyOrganization, uuid=owner.get('id'))

    CredlyBadgeTemplate.objects.update_or_create(
        uuid=badge_template.get('id'),
        defaults={
            'name': badge_template.get('name'),
            'organization': organization,
            'status': badge_template.get('state'),
            'site': get_current_request().site,
            'type': 'credly',
        }
    )


def handle_badge_template_changed_event(data):
    """
    Change the badge template.
    """
    badge_template = data.get('data', {}).get('badge_template', {})
    owner = data.get('data', {}).get('badge_template', {}).get('owner', {})

    organization = get_object_or_404(CredlyOrganization, uuid=owner.get('id'))

    CredlyBadgeTemplate.objects.update_or_create(
        uuid=badge_template.get('id'),
        defaults={
            'name': badge_template.get('name'),
            'organization': organization,
            'status': badge_template.get('state'),
            'site': get_current_request().site,
            'type': 'credly',
        }
    )


def handle_badge_template_deleted_event(data):
    """
    Deletes the badge template by provided uuid.
    """
    CredlyBadgeTemplate.objects.filter(
        uuid=data.get('data', {}).get('badge_template', {}).get('id'),
        site=get_current_request().site,
    ).delete()
