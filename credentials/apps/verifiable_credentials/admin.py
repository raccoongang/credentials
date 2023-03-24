from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .issuance.models import IssuanceLine, IssuanceConfiguration
from .toggles import is_verifiable_credentials_enabled


class IssuanceLineAdmin(admin.ModelAdmin):
    """
    Issuance line admin setup.
    """

    list_display = (
        "uuid",
        "user_credential",
        "issuer_id",
        "storage_id",
        "processed",
        "status_index",
        "status",
    )
    readonly_fields = [
        "uuid",
        "status_index",
    ]
    list_filter = ("processed",)
    search_fields = ("uuid",)


class IssuanceConfigurationForm(forms.ModelForm):
    def clean_enabled(self):
        """
        Do not allow to disable the last issuer.
        """
        # don't validate if new:
        if not self.instance.pk:
            return self.cleaned_data["enabled"]

        enabled_count = self.instance.__class__.objects.filter(enabled=True).count()
        if enabled_count < 2 and self.cleaned_data["enabled"] is False:
            raise forms.ValidationError(_("At least one Issuer must be always enabled!"))

        return self.cleaned_data["enabled"]


class IssuanceConfigurationAdmin(admin.ModelAdmin):
    """
    Issuance configuration admin setup.
    """
    form = IssuanceConfigurationForm

    list_display = [
        "issuer_id",
        "issuer_name",
        "enabled",
    ]

    def has_delete_permission(self, request, obj=None):
        return False

if is_verifiable_credentials_enabled():
    admin.site.register(IssuanceLine, IssuanceLineAdmin)
    admin.site.register(IssuanceConfiguration, IssuanceConfigurationAdmin)
