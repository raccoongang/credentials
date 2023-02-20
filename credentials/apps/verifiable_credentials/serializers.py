"""
Verifiable Credentials serializers.
"""
from rest_framework import serializers

from .models import IssuanceLine


class IssuanceLineSerializer(serializers.ModelSerializer):
    """
    Incoming issuance request default serializer.

    It is expected incoming requests from different storages to have unified shape.
    But once it is not the case, swapping this class for something more specific is possible.
    """

    class Meta:
        model = IssuanceLine
        fields = "__all__"
        read_only_fields = ["uuid", "user_credential", "processed", "issuer_id", "storage_id"]

    @staticmethod
    def swap_value(data: dict, source_key: str, target_key: str) -> None:
        data[target_key] = data.pop(source_key)

    def update(self, instance, validated_data):
        if "subject_id" not in validated_data:
            validated_data["subject_id"] = validated_data.get("holder_id")
        return super().update(instance, validated_data)
