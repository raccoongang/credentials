"""
Complementary schemas for verifiable credential composition.
"""
from rest_framework import serializers


class EducationalOccupationalProgramSchema(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Defines Open edX Program.
    """

    TYPE = "EducationalOccupationalProgram"

    type = serializers.CharField(default=TYPE, help_text="https://schema.org/EducationalOccupationalCredential")
    id = serializers.CharField(source="user_credential.credential.program_uuid")
    name = serializers.CharField(source="user_credential.credential.program.title")
    description = serializers.CharField(source="user_credential.credential.program_uuid")

    class Meta:
        read_only_fields = "__all__"


class EducationalOccupationalCredentialSchema(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Defines Open edX user credential.
    """

    name = serializers.CharField(source="user_credential.uuid")
    # description = serializers.CharField(source="user_credential.uuid")
    # awardedOnCompletionOf = EducationalOccupationalProgramSchema(source="*")

    class Meta:
        read_only_fields = "__all__"


class CredentialSubjectSchema(serializers.Serializer):  # pylint: disable=abstract-method
    TYPE = "EducationalOccupationalCredential"

    # type = serializers.CharField(default=TYPE, help_text="https://schema.org/EducationalOccupationalCredential")
    id = serializers.CharField(source="subject_id")
    # hasCredential = EducationalOccupationalCredentialSchema(source="*")
    # type = serializers.CharField(default="schema:Person")
    username = serializers.CharField(source="user_credential.username") # TODO: change to full name
    context = serializers.SerializerMethodField()

    class Meta:
        read_only_fields = "__all__"

    def to_representation(self, obj):
        primitive_repr = super().to_representation(obj)
        primitive_repr['@context'] = primitive_repr.pop('context')
        return primitive_repr

    def get_context(self, obj):
        return [
                {
                    "username": "https://schema.org/Text"
                }
            ]


class IssuerSchema(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="issuer_id")
    name = serializers.CharField(source="issuer_name")
    type = serializers.CharField(default="Issuer")

    class Meta:
        read_only_fields = "__all__"
