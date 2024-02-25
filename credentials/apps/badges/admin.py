"""
Admin section configuration.
"""

from django.contrib import admin

from .toggles import is_badges_enabled
from .models import BadgeRequirement, BadgeTemplate


class BadgeRequirementInline(admin.TabularInline):
    model = BadgeRequirement
    show_change_link = True
    extra = 0


class BadgeRequirementAdmin(admin.ModelAdmin):
    """
    Badge template requirement admin setup.
    """

    list_display = [
        "id",
        "template",
        "event_type",
        "effect",
    ]
    list_filter = [
        "template",
        "event_type",
        "effect",
    ]


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
    inlines = [
        BadgeRequirementInline,
    ]


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(BadgeTemplate, BadgeTemplateAdmin)
    admin.site.register(BadgeRequirement, BadgeRequirementAdmin)
