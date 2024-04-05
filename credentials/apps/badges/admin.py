"""
Admin section configuration.
"""

from django.contrib import admin, messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .admin_forms import CredlyOrganizationAdminForm
from .models import (
    BadgeProgress,
    BadgeRequirement,
    CredlyBadge,
    CredlyBadgeTemplate,
    CredlyOrganization,
    DataRule,
    Fulfillment,
)
from .toggles import is_badges_enabled


class BadgeRequirementInline(admin.TabularInline):
    model = BadgeRequirement
    show_change_link = True
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_active:
            readonly_fields.extend([
                "template",
                "event_type",
                "description",
            ])
        return readonly_fields

class FulfillmentInline(admin.TabularInline):
    model = Fulfillment
    extra = 0


class DataRuleInline(admin.TabularInline):
    model = DataRule
    extra = 0
    fields = [
        "data_path",
        "operator",
        "value",
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.template.is_active:
            readonly_fields.extend([
                "data_path",
                "operator",
                "value",
            ])
        return readonly_fields


class CredlyOrganizationAdmin(admin.ModelAdmin):
    """
    Credly organization admin setup.
    """

    form = CredlyOrganizationAdminForm
    list_display = (
        "name",
        "uuid",
        "api_key",
    )
    readonly_fields = [
        "name",
    ]
    actions = ("sync_organization_badge_templates",)

    @admin.action(description="Sync organization badge templates")
    def sync_organization_badge_templates(self, request, queryset):
        """
        Sync badge templates for selected organizations.
        """
        site = get_current_site(request)
        for organization in queryset:
            call_command(
                "sync_organization_badge_templates",
                organization_id=organization.uuid,
                site_id=site.id,
            )

        messages.success(request, _("Badge templates were successfully updated."))


class CredlyBadgeTemplateAdmin(admin.ModelAdmin):
    """
    Badge template admin setup.
    """

    exclude = [
        "icon",
    ]
    list_display = (
        "organization",
        "state",
        "name",
        "uuid",
        "is_active",
        "image",
    )
    list_filter = (
        "organization",
        "is_active",
        "state",
    )
    search_fields = (
        "name",
        "uuid",
    )
    readonly_fields = [
        "organization",
        "origin",
        "state",
        "dashboard_link",
        "image",
    ]
    inlines = [
        BadgeRequirementInline,
    ]

    def has_add_permission(self, request):
        return False

    def dashboard_link(self, obj):
        url = obj.management_url
        return format_html("<a href='{url}'>{url}</a>", url=url)

    def image(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="50" height="auto" />', obj.icon)
        return "-"

    image.short_description = _("icon")


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
    ]
    list_display_links = (
        "id",
        "template",
    )
    list_filter = [
        "template",
        "event_type",
    ]


    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.template.is_active:
            readonly_fields.extend([
                "template",
                "event_type",
                "description",
            ])
        return readonly_fields


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
        """
        TODO: switch dedicated `is_complete` bool field
        """
        return bool(getattr(obj, "credential", False))


class CredlyBadgeAdmin(admin.ModelAdmin):
    """
    Credly badge admin setup.
    """

    list_display = (
        "username",
        "state",
        "uuid",
    )
    list_filter = ("state",)
    search_fields = (
        "username",
        "uuid",
    )
    readonly_fields = (
        "state",
        "uuid",
    )


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(CredlyOrganization, CredlyOrganizationAdmin)
    admin.site.register(CredlyBadgeTemplate, CredlyBadgeTemplateAdmin)
    admin.site.register(CredlyBadge, CredlyBadgeAdmin)
    admin.site.register(BadgeRequirement, BadgeRequirementAdmin)
    admin.site.register(BadgeProgress, BadgeProgressAdmin)
