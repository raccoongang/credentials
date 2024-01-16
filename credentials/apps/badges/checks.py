"""
Badges checks.
"""
from django.core.checks import Error, Tags, register


@register(Tags.compatibility)
def badges_checks(*args, **kwargs):
    """
    """
    errors = []
    return errors