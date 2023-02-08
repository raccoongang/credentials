from config_models.admin import KeyedConfigurationModelAdmin
from django.conf import settings
from django.contrib import admin

from .models import IssuanceConfiguration


class IssuanceConfigurationAdmin(KeyedConfigurationModelAdmin):
    """
    Django Admin class for IssuanceConfiguration
    """

    def get_list_display(self, request):
        return (
            "enabled",
            "site",
            "slug",
            "organization",
            "digital_credential_format",
        )

if settings.ENABLE_VERIFIABLE_CREDENTIALS:
    admin.site.register(IssuanceConfiguration, IssuanceConfigurationAdmin)