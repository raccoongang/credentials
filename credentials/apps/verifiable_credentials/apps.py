# lint-amnesty, pylint: disable=missing-module-docstring

from django.apps import AppConfig
from django.conf import settings

from credentials.apps.verifiable_credentials import settings as verifiable_credentials_settings


class VerifiableCredentialsConfig(AppConfig):  # lint-amnesty, pylint: disable=missing-class-docstring
    name = "credentials.apps.verifiable_credentials"
    verbose_name = "Verifiable credentials"

    def ready(self):
        if settings.ENABLE_VERIFIABLE_CREDENTIALS:
            self._enable_verifiable_credentials()

    def _enable_verifiable_credentials(self):
        """
        Enable the use of verifiable_credentials. For configuration details, see
        credentials/apps/verifiable_credentials/settings.py.
        """

        verifiable_credentials_settings.apply_settings(settings)
