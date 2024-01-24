"""
Credly Badges admin configuration.
"""

from django.contrib import admin

from credentials.apps.badges.toggles import is_badges_enabled

from .models import CredlyOrganization


class CredlyOrganizationAdmin(admin.ModelAdmin):
    """
    Credly organization admin setup.
    """
    list_display = ("name", "uuid", "api_key",)


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(CredlyOrganization, CredlyOrganizationAdmin)
