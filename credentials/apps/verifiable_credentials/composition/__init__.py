import inspect
from collections import OrderedDict

from rest_framework import serializers

from ..settings import vc_settings


class CredentialDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    VERSION = None
    ID = None
    NAME = None

    id = serializers.UUIDField(format="urn", source="uuid", read_only=True)
    type = serializers.SerializerMethodField()

    @classmethod
    def get_context(cls):
        """
        Provide root context for all verifiable credentials.

        See: https://www.w3.org/TR/vc-data-model/#contexts
        """
        return [
            "https://www.w3.org/2018/credentials/v1",
        ]

    @classmethod
    def get_types(cls):
        """
        Provide root types for all verifiable credentials.

        See: https://www.w3.org/TR/vc-data-model/#types
        """
        return [
            "VerifiableCredential",
        ]

    @property
    def context(self):
        """
        Collects all contexts.

        - include default root context
        - include data model context
        """
        return self._collect_hierarchically(class_method="get_context")

    def get_type(self, issuance_line):
        """
        Collect all corresponding types.

        - include default root type(s)
        - include data model type(s)
        - include credential-specific type(s)
        """
        return self._collect_hierarchically(class_method="get_types") + self.resolve_credential_type(issuance_line)

    def to_representation(self, instance):
        """
        Tweak some presentation details.
        """
        credential = OrderedDict({"@context": self.context})
        credential.update(super().to_representation(instance))
        return credential

    def resolve_credential_type(self, issuance_line):
        """
        Map Open edX credential type to data model types.
        """
        credential_content_type = issuance_line.user_credential.credential_content_type.model

        credential_types = {
            # <openedx-credential-type>: [<verifiable-credential-type1>, <verifiable-credential-typeX>]
            "programcertificate": [
                "ProgramCertificate",
            ],
            "coursecertificate": [],
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
    Returns currently configured verifiable credentials data models.
    """
    return vc_settings.DEFAULT_DATA_MODELS


def get_data_model(model_id):
    for data_model in get_available_data_models():
        if data_model.ID == model_id:
            return data_model

    return None
