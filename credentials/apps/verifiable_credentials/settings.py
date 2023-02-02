"""Settings for the verifiable credentials app.

The settings contains a boolean, ENABLE_VERIFIABLE_CREDENTIALS, indicating
whether this app is enabled. Settings probes the ENABLE_VERIFIABLE_CREDENTIALS.
If true, it calls apply_settings(), passing in the Django settings
"""
from django.urls import reverse


def apply_settings(django_settings):
    django_settings.VC_DEFAULT_STANDARD = "OBv3"
    django_settings.VC_DEFAULT_STORAGE = "verifiable_credentials.storages.LCWalletStorage"
    django_settings.VC_DEFAULT_ISSUANCE_URL = django_settings.ROOT_URL + reverse("verifiable_credentials:api:v1:wallet")
