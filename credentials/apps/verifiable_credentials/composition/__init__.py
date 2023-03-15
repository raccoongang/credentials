import inspect
from collections import OrderedDict

from rest_framework import serializers


class CredentialDataModel(serializers.Serializer):  # pylint: disable=abstract-method

    VERSION = None
    ID = None
    NAME = None

    id = serializers.UUIDField(format="urn", source="uuid", read_only=True)

    @classmethod
    def get_context(cls):
        return [
            "https://www.w3.org/2018/credentials/v1",
        ]

    @property
    def context(self):
        """
        Collects all contexts.

        See: https://www.w3.org/TR/vc-data-model/#contexts
        """
        merged_context = []
        for base_class in reversed(inspect.getmro(type(self))):
            if hasattr(base_class, "get_context"):
                merged_context.extend(base_class.get_context())
        return merged_context

    def to_representation(self, instance):
        credential = OrderedDict({"@context": self.context})
        credential.update(super().to_representation(instance))
        return credential


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
