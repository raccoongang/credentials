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
    list_display = ("name", "uuid", "status", "type", "is_active",)
    list_filter = ("status", "type", "is_active",)
    search_fields = ("name", "uuid",)


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(BadgeTemplate, BadgeTemplateAdmin)
