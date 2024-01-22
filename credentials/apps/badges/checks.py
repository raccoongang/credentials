"""
Badges checks.
"""
from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.compatibility)
def badges_checks(*args, **kwargs):
    """
    Checks the consistency of the badges configurations.

    Raises compatibility Errors upon:
        - BADGES_CONFIG['events'] is empty

    Returns:
        List of any Errors.
    """
    errors = []

    if not settings.BADGES_CONFIG.get("events"):
        errors.append(
            Error(
                "BADGES_CONFIG['events'] must include at least one event.",
                hint="Add at least one event to BADGES_CONFIG['events'] setting.",
                id="badges.E001",
            )
        )

    return errors
