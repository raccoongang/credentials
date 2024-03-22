"""
Credly Badges admin configuration.
"""

from django.contrib import admin

from credentials.apps.badges.toggles import is_badges_enabled

from .forms import CredlyOrganizationAdminForm
from .models import CredlyBadge, CredlyBadgeTemplate, CredlyOrganization
from .utils import sync_badge_templates_for_organization


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
        for organization in queryset:
            sync_badge_templates_for_organization(organization.uuid)


class CredlyBadgeTemplateAdmin(admin.ModelAdmin):
    """
    Badge template admin setup.
    """

    list_display = (
        "organization",
        "state",
        "name",
        "uuid",
        "is_active",
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
        "state",
    ]


class CredlyBadgeAdmin(admin.ModelAdmin):
    """
    Credly badge admin setup.
    """
    list_display = (
        "recipient_email",
        "issuing_state",
        "uuid",
        "issued_at",
    )
    list_filter = (
        "issuing_state",
    )
    search_fields = (
        "recipient_email",
        "uuid",
    )
    readonly_fields = (
        "issuing_state",
        "uuid",
    )


if is_badges_enabled():
    admin.site.register(CredlyOrganization, CredlyOrganizationAdmin)
    admin.site.register(CredlyBadgeTemplate, CredlyBadgeTemplateAdmin)
    admin.site.register(CredlyBadge, CredlyBadgeAdmin)
