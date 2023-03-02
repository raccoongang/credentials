import logging

from django.core.management import BaseCommand
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Perform Status List issuance cycle (compose, sign, publish).
    """

    help = "Issue a new Status List credential revision for a given Issuer"

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument(
            "issuer",
            required=True,
            help=_("An Issuer on behalf of the Status List will be updated")
        )

    def handle(self, *args, **options):
        pass
