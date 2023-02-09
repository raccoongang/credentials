# lint-amnesty, pylint: disable=missing-module-docstring

from django.apps import AppConfig


class VerifiableCredentialsConfig(AppConfig):
    name = "credentials.apps.verifiable_credentials"
    verbose_name = "Verifiable Credentials"
