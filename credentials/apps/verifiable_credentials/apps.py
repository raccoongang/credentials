from django.apps import AppConfig


class VerifiableCredentialsConfig(AppConfig):
    name = "credentials.apps.verifiable_credentials"
    verbose_name = "Verifiable Credentials"

    def ready(self):
        super().ready()

        import credentials.apps.verifiable_credentials.signals  # pylint: disable=unused-import,import-outside-toplevel
