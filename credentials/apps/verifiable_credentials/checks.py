from django.core.checks import Error, Tags, register

from .settings import vc_settings


@register(Tags.compatibility)
def vc_settings_checks(*args, **kwargs):
    """
    Checks the compatibility of verifiable_credentials settings.

    Raises compatibility Errors upon:
        - No default data models defined
        - No default storages defined
        - FORCE_DATA_MODEL is not in DEFAULT_DATA_MODELS
        - DEFAULT_ISSUER_DID is not set
        - DEFAULT_ISSUER_KEY is not set

    Returns:
        List of any Errors.
    """
    errors = []

    if not vc_settings.DEFAULT_DATA_MODELS:
        errors.append(
            Error(
                "No default data models defined.",
                hint="Add at least one data model to the DEFAULT_DATA_MODELS setting.",
                id="verifiable_credentials.E001",
            )
        )

    if not vc_settings.DEFAULT_STORAGES:
        errors.append(
            Error(
                "No default storages defined.",
                hint="Add at least one storage to the DEFAULT_STORAGES setting.",
                id="verifiable_credentials.E003",
            )
        )

    if vc_settings.FORCE_DATA_MODEL and vc_settings.FORCE_DATA_MODEL not in vc_settings.DEFAULT_DATA_MODELS:
        errors.append(
            Error(
                "FORCE_DATA_MODEL is not in DEFAULT_DATA_MODELS.",
                hint="Add FORCE_DATA_MODEL to DEFAULT_DATA_MODELS setting or remove FORCE_DATA_MODEL setting.",
                id="verifiable_credentials.E002",
            )
        )

    if not vc_settings.DEFAULT_ISSUER_DID:
        errors.append(
            Error(
                "DEFAULT_ISSUER_DID is not set.",
                hint="Set DEFAULT_ISSUER_DID to a valid DID string.",
                id="verifiable_credentials.E004",
            )
        )

    if not vc_settings.DEFAULT_ISSUER_KEY:
        errors.append(
            Error(
                "DEFAULT_ISSUER_KEY is not set.",
                hint="Set DEFAULT_ISSUER_KEY to a valid key string.",
                id="verifiable_credentials.E005",
            )
        )

    return errors
