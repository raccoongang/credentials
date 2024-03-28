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
            sync_badge_templates_for_organization(organization.uuid, request.site)


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
        "username",
        "state",
        "uuid",
    )
    list_filter = (
        "state",
    )
    search_fields = (
        "username",
        "uuid",
    )
    readonly_fields = (
        "state",
        "uuid",
    )


if is_badges_enabled():
    admin.site.register(CredlyOrganization, CredlyOrganizationAdmin)
    admin.site.register(CredlyBadgeTemplate, CredlyBadgeTemplateAdmin)
    admin.site.register(CredlyBadge, CredlyBadgeAdmin)
