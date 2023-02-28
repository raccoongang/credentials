from config_models.admin import KeyedConfigurationModelAdmin
from django.contrib import admin

from .issuance import IssuanceLine
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


class IssuanceLineAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "user_credential",
        "issuer_id",
        "storage_id",
        "processed",
        "status_index"
    )
    readonly_fields = [
        "uuid",
    ]
    list_filter = ("processed",)
    search_fields = ("uuid",)


if is_verifiable_credentials_enabled():
    admin.site.register(IssuanceLine, IssuanceLineAdmin)
