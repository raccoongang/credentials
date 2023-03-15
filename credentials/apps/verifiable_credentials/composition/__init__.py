from collections import OrderedDict

from rest_framework import serializers

from ..settings import vc_settings


class BaseDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    VERSION = None
    ID = None
    NAME = None

    id = serializers.UUIDField(format="urn", source="uuid", read_only=True)

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
