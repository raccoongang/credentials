from config_models.admin import KeyedConfigurationModelAdmin
from django.contrib import admin

from .models import IssuanceConfiguration
from .toggles import is_verifiable_credentials_enabled


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


if is_verifiable_credentials_enabled():
    admin.site.register(IssuanceConfiguration, IssuanceConfigurationAdmin)
