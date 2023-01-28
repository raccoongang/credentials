"""Settings for the verifiable credentials app.

The settings contains a boolean, ENABLE_VERIFIABLE_CREDENTIALS, indicating
whether this app is enabled. Settings probes the ENABLE_VERIFIABLE_CREDENTIALS.
If true, it calls apply_settings(), passing in the Django settings
"""


def apply_settings(django_settings):
    django_settings.VC_DEFAULT_STANDARD = "OBv3"
