"""
Badges app self-checks.
"""

from django.core.checks import Error, Tags, register

from .utils import get_badging_event_types


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

    if not get_badging_event_types():
        errors.append(
            Error(
                "BADGES_CONFIG['events'] must include at least one event.",
                hint="Add at least one event to BADGES_CONFIG['events'] setting.",
                id="badges.E001",
            )
        )

    return errors
