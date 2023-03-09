from collections import OrderedDict

from rest_framework import serializers


class BaseDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.UUIDField(format="urn", source="uuid", read_only=True)

    def to_representation(self, instance):
        credential = OrderedDict({"@context": self.context})
        credential.update(super().to_representation(instance))
        return credential
