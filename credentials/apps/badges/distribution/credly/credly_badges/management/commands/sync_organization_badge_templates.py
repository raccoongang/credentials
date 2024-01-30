import logging
from django.core.management.base import BaseCommand
from credly_badges.utils import sync_badge_templates_for_organization
from credly_badges.models import CredlyOrganization


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync badge templates for a specific organization or all organizations'

    def add_arguments(self, parser):
        parser.add_argument('--organization_id', type=str, help='UUID of the organization.')

    def handle(self, *args, **options):
        """
        Sync badge templates for a specific organization or all organizations.

        Usage:
            ./manage.py sync_organization_badge_templates
            ./manage.py sync_organization_badge_templates --organization_id c117c179-81b1-4f7e-a3a1-e6ae30568c13
        """
        organization_id = options.get('organization_id')

        if organization_id:
            logger.info(f'Syncing badge templates for single organization: {organization_id}')
            sync_badge_templates_for_organization(organization_id)
        else:
            all_organization_ids = CredlyOrganization.get_all_organization_ids()
            logger.info(f'Organization id was not provided. Syncing badge templates for all organizations: {all_organization_ids}')
            for organization_id in all_organization_ids:
                sync_badge_templates_for_organization(organization_id)

        logger.info('Done.')
