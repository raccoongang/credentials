from rest_framework import serializers


class ProgramCredentialSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    uuid = serializers.UUIDField(read_only=True)
    status = serializers.CharField(max_length=255, read_only=True)
    username = serializers.CharField(max_length=255, read_only=True)
    download_url = serializers.CharField(max_length=255, read_only=True)
    credential_id = serializers.IntegerField(read_only=True)
    program_uuid = serializers.UUIDField(read_only=True)
    program_title = serializers.CharField(max_length=255, read_only=True)
    program_org = serializers.CharField(max_length=255, read_only=True)
    modified_date = serializers.DateTimeField()


class StorageSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(max_length=255, read_only=True)
    name = serializers.CharField(max_length=255, read_only=True)
