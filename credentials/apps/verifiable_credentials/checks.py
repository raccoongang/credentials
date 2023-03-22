from django.core.checks import Error, Tags, register

from .settings import vc_settings
from .toggles import ENABLE_VERIFIABLE_CREDENTIALS


@register(Tags.compatibility)
def vc_settings_checks(*args, **kwargs):
    """
    Checks the consistency of the verifiable_credentials settings.

    Raises compatibility Errors upon:
        - No default data models defined
        - No default storages defined
        - FORCE_DATA_MODEL is not in DEFAULT_DATA_MODELS
        - DEFAULT_ISSUER[DID] is not set
        - DEFAULT_ISSUER[KEY] is not set

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

    if not vc_settings.DEFAULT_ISSUER.get("ID"):
        errors.append(
            Error(
                f"DEFAULT_ISSUER[DID] is mandatory when {ENABLE_VERIFIABLE_CREDENTIALS.name} is True.",
                hint=" Set DEFAULT_ISSUER[DID] to a valid DID string.",
                id="verifiable_credentials.E004",
            )
        )

    if not vc_settings.DEFAULT_ISSUER.get("KEY"):
        errors.append(
            Error(
                f"DEFAULT_ISSUER_KEY is mandatory when {ENABLE_VERIFIABLE_CREDENTIALS.name} is True.",
                hint="Set DEFAULT_ISSUER_KEY to a valid key string.",
                id="verifiable_credentials.E005",
            )
        )

    return errors
