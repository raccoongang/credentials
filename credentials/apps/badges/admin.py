"""
Admin section configuration.
"""

from django.contrib import admin

from .toggles import is_badges_enabled
from .models import BadgeTemplate


class BadgeTemplateAdmin(admin.ModelAdmin):
    """
    Badge template admin setup.
    """

    list_display = (
        "name",
        "uuid",
        "origin",
        "is_active",
    )
    list_filter = (
        "is_active",
        "origin",
    )
    search_fields = (
        "name",
        "uuid",
    )
    readonly_fields = [
        "origin",
    ]


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(BadgeTemplate, BadgeTemplateAdmin)
