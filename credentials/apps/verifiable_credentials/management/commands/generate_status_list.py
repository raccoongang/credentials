""" Generate status list. """

import logging

from django.core.management import BaseCommand

from credentials.apps.verifiable_credentials.utils import generate_status_list


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate status list"

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument("issuer_did", type=str, help="The issuer DID")

    def handle(self, *args, **options):
        issuer_did = options.get("issuer_did")
        generate_status_list(issuer_did)
