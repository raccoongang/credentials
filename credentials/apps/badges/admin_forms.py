"""
Badges admin forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .credly.api_client import CredlyAPIClient
from .credly.exceptions import CredlyAPIError
from .models import BadgePenalty, BadgeRequirement, CredlyOrganization, DataRule, PenaltyDataRule


class CredlyOrganizationAdminForm(forms.ModelForm):
    """
    Additional actions for Credly Organization items.
    """

    api_data = {}

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

    def save(self, commit=True):
        """
        Auto-fill addition properties.
        """
        instance = super().save(commit=False)
        instance.name = self.api_data.get("name")
        instance.save()

        return instance

    def _ensure_organization_exists(self, api_client):
        """
        Try to fetch organization data by the configured Credly Organization ID.
        """
        try:
            response_json = api_client.fetch_organization()
            if org_data := response_json.get("data"):
                self.api_data = org_data
        except CredlyAPIError as err:
            raise forms.ValidationError(message=str(err))


            
class BadgePenaltyForm(forms.ModelForm):
    class Meta:
        model = BadgePenalty
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'template') and self.instance.template.is_active:
            for field_name in self.fields:
                if field_name in ("template", "requirements", "description", "event_type"):
                    self.fields[field_name].disabled = True


class PenaltyDataRuleForm(forms.ModelForm):
    class Meta:
        model = PenaltyDataRule
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'penalty') and self.instance.penalty.template.is_active:
            for field_name in self.fields:
                if field_name in ("data_path", "operator", "value"):
                    self.fields[field_name].disabled = True
            

class BadgeRequirementForm(forms.ModelForm):
    class Meta:
        model = BadgeRequirement
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'template') and self.instance.template.is_active:
            for field_name in self.fields:
                if field_name in ("template", "event_type", "description", "group"):
                    self.fields[field_name].disabled = True


class DataRuleForm(forms.ModelForm):
    class Meta:
        model = DataRule
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'requirement') and self.instance.requirement.template.is_active:
            for field_name in self.fields:
                if field_name in ("data_path", "operator", "value"):
                    self.fields[field_name].disabled = True
