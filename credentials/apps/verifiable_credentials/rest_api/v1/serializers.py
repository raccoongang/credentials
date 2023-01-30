from rest_framework import serializers


class ProgramCredentialSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    uuid = serializers.UUIDField()
    status = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    download_url = serializers.CharField(max_length=255)
    credential_id = serializers.IntegerField()
    program_uuid = serializers.UUIDField()
    program_title = serializers.CharField(max_length=255)
