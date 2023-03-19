from django.contrib import admin

from .issuance import IssuanceLine
from .toggles import is_verifiable_credentials_enabled


class IssuanceLineAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "user_credential",
        "issuer_id",
        "storage_id",
        "processed",
    )
    readonly_fields = [
        "uuid",
    ]
    list_filter = ("processed",)
    search_fields = ("uuid",)


if is_verifiable_credentials_enabled():
    admin.site.register(IssuanceLine, IssuanceLineAdmin)
