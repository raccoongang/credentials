from rest_framework import serializers


class StorageSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(max_length=255, source="ID")
    name = serializers.CharField(max_length=255, source="VERBOSE_NAME")

    class Meta:
        read_only_fields = "__all__"
