"""
Django forms for the credly badges
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CredlyOrganization
from .rest_api import CredlyAPIClient
from .exceptions import CredlyAPIError

class CredlyOrganizationAdminForm(forms.ModelForm):
    class Meta:
        model = CredlyOrganization
        fields = "__all__"

    def clean(self):
        """
        Validate that organization is existing on Credly services.
        """
        cleaned_data = super().clean()

        uuid = cleaned_data.get("uuid")
        api_key = cleaned_data.get("api_key")

        try:
            credly_api_client = CredlyAPIClient(uuid, api_key)
            credly_api_client.fetch_organization()
        except CredlyAPIError:
            raise forms.ValidationError(_('Invalid organization ID or API key. Organization not found on Credly services.'))

        return cleaned_data
