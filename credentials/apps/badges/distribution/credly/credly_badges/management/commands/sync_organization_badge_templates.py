import logging

from credly_badges.models import CredlyOrganization
from credly_badges.utils import sync_badge_templates_for_organization
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync badge templates for a specific organization or all organizations"

    def add_arguments(self, parser):
        parser.add_argument("--site_id", type=int, help="Site ID.")
        parser.add_argument("--organization_id", type=str, help="UUID of the organization.")

    def handle(self, *args, **options):
        """
        Sync badge templates for a specific organization or all organizations.

        Usage:
            ./manage.py sync_organization_badge_templates --site_id 1
            ./manage.py sync_organization_badge_templates --site_id 1 --organization_id c117c179-81b1-4f7e-a3a1-e6ae30568c13
        """

        organization_id = options.get("organization_id")
        site_id = options.get("site_id")
        try:
            site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            logger.info(f"Site with id {site_id} does not exists")

        if organization_id:
            logger.info(f"Syncing badge templates for single organization: {organization_id}")
            sync_badge_templates_for_organization(organization_id, site)
        else:
            all_organization_ids = CredlyOrganization.get_all_organization_ids()
            logger.info(
                f"Organization id was not provided. Syncing badge templates for all organizations: {all_organization_ids}"
            )
            for organization_id in all_organization_ids:
                sync_badge_templates_for_organization(organization_id, site)

        logger.info("Done.")
