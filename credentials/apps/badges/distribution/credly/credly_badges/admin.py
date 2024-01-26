"""
Credly Badges admin configuration.
"""

from django.contrib import admin

from credentials.apps.badges.toggles import is_badges_enabled

from .forms import CredlyOrganizationAdminForm
from .models import BadgeTemplate, CredlyOrganization
from .utils import sync_badge_templates_for_organization


class CredlyOrganizationAdmin(admin.ModelAdmin):
    """
    Credly organization admin setup.
    """
    form = CredlyOrganizationAdminForm
    list_display = ("name", "uuid", "api_key",)
    actions = ("sync_organization_badge_templates",)

    @admin.action(description="Sync organization badge templates")
    def sync_organization_badge_templates(self, request, queryset):
        """
        Sync badge templates for selected organizations.
        """
        for organization in queryset:
            sync_badge_templates_for_organization(organization.uuid)


class BadgeTemplateAdmin(admin.ModelAdmin):
    """
    Badge template admin setup.
    """
    list_display = ("name", "uuid", "organization", "state",)
    list_filter = ("state", "organization",)
    search_fields = ("name", "uuid",)


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(CredlyOrganization, CredlyOrganizationAdmin)
    admin.site.register(BadgeTemplate, BadgeTemplateAdmin)
