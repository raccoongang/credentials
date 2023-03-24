from django.apps import AppConfig

from .toggles import is_verifiable_credentials_enabled


class VerifiableCredentialsConfig(AppConfig):
    name = "credentials.apps.verifiable_credentials"
    verbose_name = "Verifiable Credentials"

    def ready(self):
        """
        Performs initial registrations for checks, signals, etc.
        """
        if is_verifiable_credentials_enabled():
            from . import signals  # pylint: disable=unused-import,import-outside-toplevel
            from .checks import vc_settings_checks  # pylint: disable=unused-import,import-outside-toplevel
            from .issuance.models import create_issuers
            from .issuance.status_list import issue_status_lists

            create_issuers()
            issue_status_lists()
