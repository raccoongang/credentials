"""
Admin section configuration for credly badges.
"""

from django.contrib import admin

from .toggles import is_credly_badges_enabled
from .models import CredlyOrganization


class CredlyOrganizationAdmin(admin.ModelAdmin):
    """
    Credly organization admin setup.
    """
    list_display = ("name", "uuid", "api_key",)


if is_credly_badges_enabled():
    admin.site.register(CredlyOrganization, CredlyOrganizationAdmin)
