"""
Badges admin forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from credentials.apps.badges.credly.api_client import CredlyAPIClient
from credentials.apps.badges.credly.exceptions import CredlyAPIError
from credentials.apps.badges.models import AbstractDataRule, BadgePenalty, BadgeRequirement, CredlyOrganization, DataRule, PenaltyDataRule
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
    """
    Form for BadgePenalty model.
    """
    class Meta:
        model = BadgePenalty
        fields = "__all__"

    def clean(self):
        """
        Ensure that all penalties belong to the same template.
        """
        cleaned_data = super().clean()
        requirements = cleaned_data.get("requirements")

        if requirements and not all(
            [requirement.template.id == cleaned_data.get("template").id for requirement in requirements]
        ):
            raise forms.ValidationError(_("All requirements must belong to the same template."))
        return cleaned_data


class DataRuleBoolValidationMixin:
    """
    Mixin for DataRule form to validate boolean fields.
    """

    def clean(self):
        """
        Validate boolean fields.
        """

        cleaned_data = super().clean()

        last_key = cleaned_data.get("data_path").split(".")[-1]
        if "is_" in last_key and cleaned_data.get("value") not in AbstractDataRule.BOOL_VALUES:
            raise forms.ValidationError(_("Value must be a boolean."))
        
        return cleaned_data


class DataRuleFormSet(forms.BaseInlineFormSet):
    """
    Formset for DataRule model.
    """
    def get_form_kwargs(self, index):
        """
        Pass parent instance to the form.
        """

        kwargs = super().get_form_kwargs(index)
        kwargs["parent_instance"] = self.instance
        return kwargs


class DataRuleForm(DataRuleBoolValidationMixin, forms.ModelForm):
    """
    Form for DataRule model.
    """
    class Meta:
        model = DataRule
        fields = "__all__"

    data_path = forms.ChoiceField()

    def __init__(self, *args, parent_instance=None, **kwargs):
        """
        Load data paths based on the parent instance event type.
        """
        self.parent_instance = parent_instance
        super().__init__(*args, **kwargs)

        if self.parent_instance:
            event_type = self.parent_instance.event_type
            self.fields["data_path"].choices = Choices(*get_event_type_keypaths(event_type=event_type))


class BadgeRequirementFormSet(forms.BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["parent_instance"] = self.instance
        return kwargs


class BadgeRequirementForm(forms.ModelForm):
    class Meta:
        model = BadgeRequirement
        fields = "__all__"

    group = forms.ChoiceField()

    def __init__(self, *args, parent_instance=None, **kwargs):
        self.template = parent_instance
        super().__init__(*args, **kwargs)

        self.fields["group"].choices = Choices(
            *[(chr(i), chr(i)) for i in range(65, 91)]
        )
        self.fields["group"].initial = chr(65 + self.template.requirements.count())


class PenaltyDataRuleFormSet(forms.BaseInlineFormSet):
    """
    Formset for PenaltyDataRule model.
    """
    def get_form_kwargs(self, index):
        """
        Pass parent instance to the form.
        """

        kwargs = super().get_form_kwargs(index)
        kwargs["parent_instance"] = self.instance
        return kwargs


class PenaltyDataRuleForm(DataRuleBoolValidationMixin, forms.ModelForm):
    """
    Form for PenaltyDataRule model.
    """

    class Meta:
        model = PenaltyDataRule
        fields = "__all__"

    data_path = forms.ChoiceField()

    def __init__(self, *args, parent_instance=None, **kwargs):
        """
        Load data paths based on the parent instance event type.
        """
        self.parent_instance = parent_instance
        super().__init__(*args, **kwargs)

        if self.parent_instance:
            event_type = self.parent_instance.event_type
            self.fields["data_path"].choices = Choices(*get_event_type_keypaths(event_type=event_type))
