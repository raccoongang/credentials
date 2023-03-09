from django.apps import AppConfig


class VerifiableCredentialsConfig(AppConfig):
    name = "credentials.apps.verifiable_credentials"
    verbose_name = "Verifiable Credentials"

    def ready(self):
        super().ready()

        from .checks import vc_settings_checks  # pylint: disable=unused-import,import-outside-toplevel
