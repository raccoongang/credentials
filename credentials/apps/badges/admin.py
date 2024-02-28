"""
Admin section configuration.
"""

from django.contrib import admin

from .models import BadgeRequirement, BadgeTemplate, DataRule
from .toggles import is_badges_enabled


class BadgeRequirementInline(admin.TabularInline):
    model = BadgeRequirement
    show_change_link = True
    extra = 0


class DataRuleInline(admin.TabularInline):
    model = DataRule
    extra = 0


class BadgeRequirementAdmin(admin.ModelAdmin):
    """
    Badge template requirement admin setup.
    """

    inlines = [
        DataRuleInline,
    ]

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

    inlines = [
        BadgeRequirementInline,
    ]

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
    admin.site.register(BadgeRequirement, BadgeRequirementAdmin)
