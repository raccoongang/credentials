"""
Badges admin forms.
"""

import inspect

from django import forms
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from credentials.apps.badges.credly.api_client import CredlyAPIClient
from credentials.apps.badges.credly.exceptions import CredlyAPIError
from credentials.apps.badges.models import BadgePenalty, CredlyOrganization, DataRule
from credentials.apps.badges.utils import get_event_type_keypaths


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

    def clean(self):
        cleaned_data = super().clean()
        requirements = cleaned_data.get("requirements")

        if requirements and not all(
            [requirement.template.id == cleaned_data.get("template").id for requirement in requirements]
        ):
            raise forms.ValidationError("All requirements must belong to the same template.")
        return cleaned_data


class DataRuleFormSet(forms.BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["parent_instance"] = self.instance
        return kwargs


class DataRuleForm(forms.ModelForm):
    class Meta:
        model = DataRule
        fields = "__all__"

    data_path = forms.ChoiceField()

    def __init__(self, *args, parent_instance=None, **kwargs):
        self.parent_instance = parent_instance
        super().__init__(*args, **kwargs)

        if self.parent_instance:
            event_type = self.parent_instance.event_type
            self.fields["data_path"].choices = Choices(*get_event_type_keypaths(event_type=event_type))
