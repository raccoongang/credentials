import logging

from django.core.management.base import BaseCommand

from credentials.apps.badges.accredible.api_client import AccredibleAPIClient
from credentials.apps.badges.models import AccredibleAPIConfig


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync badge templates for a specific organization or all organizations"

    def add_arguments(self, parser):
        parser.add_argument("--site_id", type=int, help="Site ID.")
        parser.add_argument("--api_config_id", type=str, help="ID of the API config.")

    def handle(self, *args, **options):
        """
        Sync groups for a specific accredible api config or all configs.

        Usage:
            site_id=1
            api_config_id=1

            ./manage.py sync_organization_badge_templates --site_id $site_id
            ./manage.py sync_organization_badge_templates --site_id $site_id --api_config_id $api_config_id
        """
        DEFAULT_SITE_ID = 1
        api_configs_to_sync = []

        site_id = options.get("site_id")
        api_config_id = options.get("api_config_id")

        if site_id is None:
            logger.warning(f"Side ID wasn't provided: assuming site_id = {DEFAULT_SITE_ID}")
            site_id = DEFAULT_SITE_ID

        if api_config_id:
            api_configs_to_sync.append(api_config_id)
            logger.info(f"Syncing groups for the single config: {api_config_id}")
        else:
            api_configs_to_sync = AccredibleAPIConfig.get_all_api_config_ids()
            logger.info(
                "API Config ID wasn't provided: syncing groups for all configs - "
                f"{api_configs_to_sync}",
            )

        for api_config_id in api_configs_to_sync:
            api_config = AccredibleAPIConfig.objects.get(id=api_config_id)
            accredible_api_client = AccredibleAPIClient(api_config)
            processed_items = accredible_api_client.sync_groups(site_id)

            logger.info(f"API Config {api_config_id}: got {processed_items} groups.")

        logger.info("...completed!")
