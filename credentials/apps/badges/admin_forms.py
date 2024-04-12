"""
Badges admin forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .credly.api_client import CredlyAPIClient
from .credly.exceptions import CredlyAPIError
from .models import BadgePenalty, BadgeRequirement, BadgeTemplate, CredlyOrganization, DataRule, PenaltyDataRule


class BadgeTemplteValidationMixin:
    def clean(self):
        cleaned_data = super().clean()
        if self.instance.is_active:
            raise forms.ValidationError("Configuration updates are blocked on active badge templates")
        return cleaned_data


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


class BadgePenaltyForm(BadgeTemplteValidationMixin, forms.ModelForm):
    class Meta:
        model = BadgePenalty
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and hasattr(self.instance, "template"):
            if self.instance.template.is_active:
                for field_name in ("event_type", "template", "requirements", "description"):
                    self.fields[field_name].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        requirements = cleaned_data.get("requirements")

        if requirements and not all(
            [requirement.template.id == cleaned_data.get("template").id for requirement in requirements]
        ):
            raise forms.ValidationError("All requirements must belong to the same template.")
        return cleaned_data


class PenaltyDataRuleForm(BadgeTemplteValidationMixin, forms.ModelForm):
    class Meta:
        model = PenaltyDataRule
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "penalty") and self.instance.is_active:
            for field_name in self.fields:
                if field_name in ("data_path", "operator", "value"):
                    self.fields[field_name].disabled = True


class BadgeRequirementForm(BadgeTemplteValidationMixin, forms.ModelForm):
    class Meta:
        model = BadgeRequirement
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "template") and self.instance.is_active:
            for field_name in self.fields:
                if field_name in ("template", "event_type", "description", "group"):
                    self.fields[field_name].disabled = True


class DataRuleForm(BadgeTemplteValidationMixin, forms.ModelForm):
    class Meta:
        model = DataRule
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "requirement") and self.instance.is_active:
            for field_name in self.fields:
                if field_name in ("data_path", "operator", "value"):
                    self.fields[field_name].disabled = True


class BadgeTemplateForm(forms.ModelForm):
    class Meta:
        model = BadgeTemplate
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        if cleaned_data.get("is_active") and not self.instance.badgerequirement_set.exists():
            raise forms.ValidationError("Badge Template must have at least 1 Requirement set.")
        return cleaned_data
