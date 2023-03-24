import inspect
from collections import OrderedDict

from rest_framework import serializers

from ..settings import vc_settings


class CredentialDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Basic credential construction machinery.

    NOTE: it is not intended for direct inheritance, use VerifiableCredentialsDataModel instead.
    """

    VERSION = None
    ID = None
    NAME = None

    def collect_context(self, __):
        """
        Collect contexts.

        - include default root context
        - include data model context
        """
        return self._collect_hierarchically(class_method="get_context")

    def get_type(self, issuance_line):
        """
        Collect corresponding types.

        - include default root type(s)
        - include data model type(s)
        - include credential-specific type(s)
        """
        data_model_types = self._collect_hierarchically(class_method="get_types")
        credential_types = self.resolve_credential_type(issuance_line)
        return data_model_types + credential_types

    def resolve_credential_type(self, issuance_line):
        """
        Map Open edX credential type to data model types.

        Decides: which types should be included based on the source Open edX credential type.
        See:
            https://w3c.github.io/vc-imp-guide/#creating-new-credential-types
            https://schema.org/EducationalOccupationalCredential
        """
        if not issuance_line.user_credential:
            return []

        credential_content_type = issuance_line.user_credential.credential_content_type.model

        # configuration: Open edX internal credential type <> verifiable credential type
        credential_types = {
            "programcertificate": [
                "EducationalOccupationalCredential",
            ],
            "coursecertificate": [
                "EducationalOccupationalCredential",
            ],
        }

        if credential_content_type not in credential_types:
            return []

        return credential_types[credential_content_type]

    def _collect_hierarchically(self, class_method):
        """
        Call given method through model MRO and collect returned values.
        """
        values = OrderedDict()
        reversed_mro_classes = reversed(inspect.getmro(type(self)))
        for base_class in reversed_mro_classes:
            if hasattr(base_class, class_method):
                values_list = getattr(base_class, class_method)()
                for value in values_list:
                    values[value] = base_class.__name__
        return list(values.keys())


def get_available_data_models():
    """
    Return available for users verifiable credentials data models.
    """
    # NOTE(open-edx wallet): currently, Status List is available for manual issuance for the onboarding purposes.
    return get_data_models()


def get_data_models():
    """
    Return configured verifiable credentials data models.
    """
    return vc_settings.DEFAULT_DATA_MODELS + [
        vc_settings.STATUS_LIST_DATA_MODEL,
    ]


def get_data_model(model_id):
    """
    Return a data model by its ID from the currently available list.
    """
    for data_model in get_data_models():
        if data_model.ID == model_id:
            return data_model

    return None
