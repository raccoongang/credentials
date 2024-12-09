"""
Complementary schemas for verifiable credential composition.
"""

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType


class EducationalOccupationalProgramSchema(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Defines Open edX Program.
    """

    TYPE = "EducationalOccupationalProgram"

    id = serializers.CharField(default=TYPE, help_text="https://schema.org/EducationalOccupationalProgram")
    name = serializers.CharField(source="user_credential.credential.program.title")
    description = serializers.CharField(source="user_credential.credential.program_uuid")

    class Meta:
        read_only_fields = "__all__"


class EducationalOccupationalCourseSchema(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Defines Open edX Course.
    """

    TYPE = "Course"

    id = serializers.CharField(default=TYPE, help_text="https://schema.org/Course")
    name = serializers.CharField(source="course.title")
    courseCode = serializers.CharField(source="user_credential.credential.course_id")

    class Meta:
        read_only_fields = "__all__"


class EducationalOccupationalCredentialSchema(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Defines Open edX user credential.
    """

    TYPE = "EducationalOccupationalCredential"

    id = serializers.CharField(default=TYPE, help_text="https://schema.org/EducationalOccupationalCredential")
    name = serializers.CharField(source="user_credential.credential.title")
    description = serializers.CharField(source="user_credential.uuid")
    program = EducationalOccupationalProgramSchema(source="*")
    course = EducationalOccupationalCourseSchema(source="*")

    def to_representation(self, instance):
        """
        Dynamically remove fields based on the type before serialization.
        """
        program_content_type = ContentType.objects.get(app_label="credentials", model="programcertificate")
        if instance.user_credential.credential_content_type == program_content_type:
            self.fields.pop("course", None)
        else:
            self.fields.pop("program", None)

        return super().to_representation(instance)

    class Meta:
        read_only_fields = "__all__"


class CredentialSubjectSchema(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="subject_id")
    hasCredential = EducationalOccupationalCredentialSchema(source="*")

    class Meta:
        read_only_fields = "__all__"


class IssuerSchema(serializers.Serializer):  # pylint: disable=abstract-method
    TYPE = "Profile"

    id = serializers.CharField(source="issuer_id")
    type = serializers.CharField(default=TYPE)
    name = serializers.CharField(source="issuer_name")

    class Meta:
        read_only_fields = "__all__"
