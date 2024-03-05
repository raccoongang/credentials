"""
Admin section configuration.
"""

from django.contrib import admin

from .models import (
    BadgeProgress,
    BadgeRequirement,
    BadgeTemplate,
    DataRule,
    Fulfillment,
)
from .toggles import is_badges_enabled


class BadgeRequirementInline(admin.TabularInline):
    model = BadgeRequirement
    show_change_link = True
    extra = 0


class FulfillmentInline(admin.TabularInline):
    model = Fulfillment
    extra = 0


class DataRuleInline(admin.TabularInline):
    model = DataRule
    extra = 0
    readonly_fields = ("operator",)
    fields = [
        "path",
        "operator",
        "value",
    ]


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


class BadgeProgressAdmin(admin.ModelAdmin):
    """
    Badge template progress admin setup.
    """

    inlines = [
        FulfillmentInline,
    ]
    list_display = [
        "id",
        "template",
        "username",
        "complete",
    ]
    list_display_links = (
        "id",
        "template",
    )

    @admin.display(boolean=True)
    def complete(self, obj):
        return bool(getattr(obj, "credential", False))  # FIXME: optimize 100+1


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(BadgeTemplate, BadgeTemplateAdmin)
    admin.site.register(BadgeRequirement, BadgeRequirementAdmin)
    admin.site.register(BadgeProgress, BadgeProgressAdmin)
