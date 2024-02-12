"""
Credly Badges admin forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .api_client import CredlyAPIClient
from .exceptions import CredlyAPIError
from .models import CredlyOrganization


class CredlyOrganizationAdminForm(forms.ModelForm):
    """
    Additional actions for Credly Organization items.
    """

    class Meta:
        model = CredlyOrganization
        fields = "__all__"

    def clean(self):
        """
        Perform Credly API check for given organization ID.

        - Credly Organization exists;
        - fetch additional data for such organization;
        """
        cleaned_data = super().clean()

        uuid = cleaned_data.get("uuid")
        api_key = cleaned_data.get("api_key")

        credly_api_client = CredlyAPIClient(uuid, api_key)
        self._ensure_organization_exists(credly_api_client)

        return cleaned_data

    def _ensure_organization_exists(self, api_client):
        """
        Try to fetch organization data by the configured Credly Organization ID.
        """
        try:
            return api_client.fetch_organization()
        except CredlyAPIError as exc:
            raise forms.ValidationError(exc)
