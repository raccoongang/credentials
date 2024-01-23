"""
Toggles for credly badges app.
"""

from edx_toggles.toggles import SettingToggle

# .. toggle_name: CREDLY_BADGES_ENABLED
# .. toggle_implementation: DjangoSetting
# .. toggle_default: False
# .. toggle_description: Determines if the Credentials IDA uses credly badges functionality.
# .. toggle_life_expectancy: permanent
# .. toggle_permanent_justification: Credly badges are optional for usage.
# .. toggle_creation_date: 2024-01-16
# .. toggle_use_cases: open_edx
ENABLE_CREDLY_BADGES = SettingToggle('CREDLY_BADGES_ENABLED', default=False, module_name=__name__)


def is_credly_badges_enabled():
    """
    Checks if credly badges app enabled.
    """
    return ENABLE_CREDLY_BADGES.is_enabled()


def check_credly_badges_enabled(func):
    """
    Decorator for checking the applicability of a credly badges app.
    """
    def wrapper(*args, **kwargs):
        if is_credly_badges_enabled():
            return func(*args, **kwargs)
    return wrapper
