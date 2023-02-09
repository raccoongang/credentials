from config_models.admin import KeyedConfigurationModelAdmin
from django.conf import settings
from django.contrib import admin

from .models import IssuanceConfiguration, VerifiableCredentialIssuance


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


class VerifiableCredentialIssuanceAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user_credential", "issuer_did", "processed")
    list_filter = ("processed",)
    search_fields = ("uuid",)


if settings.ENABLE_VERIFIABLE_CREDENTIALS:
    admin.site.register(IssuanceConfiguration, IssuanceConfigurationAdmin)
    admin.site.register(VerifiableCredentialIssuance, VerifiableCredentialIssuanceAdmin)
