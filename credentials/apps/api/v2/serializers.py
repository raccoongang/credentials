"""
Serializers for data manipulated by the credentials service APIs.
"""
import ast
import logging
from pathlib import Path
from typing import Dict, Generator, List, Union

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.datastructures import MultiValueDict
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from credentials.apps.api.accreditors import Accreditor
from credentials.apps.catalog.models import CourseRun
from credentials.apps.credentials.constants import UserCredentialStatus
from credentials.apps.credentials.models import (
    CourseCertificate,
    ProgramCertificate,
    Signatory,
    UserCredential,
    UserCredentialAttribute,
    UserCredentialDateOverride,
)
from credentials.apps.records.models import UserGrade


logger = logging.getLogger(__name__)


class CredentialField(serializers.Field):
    """Field identifying the credential type and identifiers."""

    def to_internal_value(self, data):
        site = self.context["request"].site

        program_uuid = data.get("program_uuid")
        if program_uuid:
            try:
                return ProgramCertificate.objects.get(program_uuid=program_uuid, is_active=True)
            except ObjectDoesNotExist:
                msg = f"No active ProgramCertificate exists for program [{program_uuid}]"
                logger.exception(msg)
                raise ValidationError({"program_uuid": msg})

        course_run_key = data.get("course_run_key")
        if course_run_key:
            if self.read_only:
                try:
                    cert = CourseCertificate.objects.get(course_id=course_run_key, site=site)
                except ObjectDoesNotExist:
                    cert = None
            else:
                try:
                    course_run = CourseRun.objects.get(key=course_run_key)
                except ObjectDoesNotExist:
                    logger.exception(
                        "Course run certificate failed to create "
                        f"because the course run [{course_run_key}] doesn't exist in the catalog"
                    )
                    # TODO: course_run is still nullable while we validate the data. Re raise the exception once the
                    # field is no longer nullable
                    course_run = None
                # Create course cert on the fly, but don't upgrade it to active if it's manually been turned off
                cert, _ = CourseCertificate.objects.get_or_create(
                    course_id=course_run_key,
                    course_run=course_run,
                    site=site,
                    defaults={
                        "is_active": True,
                        "certificate_type": data.get("mode"),
                    },
                )

            if cert is None or not cert.is_active:
                msg = f"No active CourseCertificate exists for course run [{course_run_key}]"
                logger.exception(msg)
                raise ValidationError({"course_run_key": msg})

            return cert

        raise ValidationError("Credential identifier is missing.")

    def to_representation(self, value):
        """Serialize objects to a according to model content-type."""
        if hasattr(value, "program_uuid"):
            credential = {
                "type": "program",
                "credential_id": value.id,
                "program_uuid": value.program_uuid,
            }
        else:  # course run
            credential = {
                "type": "course-run",
                "course_run_key": value.course_id,
                "mode": value.certificate_type,
            }

        return credential


class UserCertificateURLField(serializers.ReadOnlyField):  # pylint: disable=abstract-method
    """Field for UserCredential URL pointing html view"""

    def to_representation(self, value):
        """Build the UserCredential URL for html view. Get the current domain from request."""
        return reverse(
            "credentials:render",
            kwargs={
                "uuid": value.hex,
            },
            request=self.context["request"],
        )


class CourseRunField(serializers.Field):
    """Field for CourseRun foreign keys"""

    def to_internal_value(self, data):
        site = self.context["request"].site
        try:
            return CourseRun.objects.get(key=data, course__site=site)
        except ObjectDoesNotExist:
            msg = f"No CourseRun exists for key [{data}]"
            logger.exception(msg)
            raise ValidationError(msg)

    def to_representation(self, value):
        """Build the CourseRun for html view."""
        return value.key


class UserCredentialAttributeSerializer(serializers.ModelSerializer):
    """Serializer for CredentialAttribute objects"""

    class Meta:
        model = UserCredentialAttribute
        fields = ("name", "value")


class UserCredentialDateOverrideSerializer(serializers.ModelSerializer):
    """Serializer for UserCredentialDateOverride objects"""

    class Meta:
        model = UserCredentialDateOverride
        fields = ("date",)


class UserCredentialSerializer(serializers.ModelSerializer):
    """Serializer for UserCredential objects."""

    credential = CredentialField(read_only=True)
    attributes = UserCredentialAttributeSerializer(many=True, read_only=True)
    date_override = UserCredentialDateOverrideSerializer(required=False, allow_null=True)
    certificate_url = UserCertificateURLField(source="uuid", read_only=True)

    class Meta:
        model = UserCredential
        fields = (
            "username",
            "credential",
            "status",
            "download_url",
            "uuid",
            "attributes",
            "date_override",
            "created",
            "modified",
            "certificate_url",
        )
        read_only_fields = (
            "username",
            "download_url",
            "uuid",
            "created",
            "modified",
        )


class UserCredentialCreationSerializer(serializers.ModelSerializer):
    """Serializer used to create UserCredential objects."""

    credential = CredentialField()
    attributes = UserCredentialAttributeSerializer(many=True, required=False)
    date_override = UserCredentialDateOverrideSerializer(required=False, allow_null=True)
    certificate_url = UserCertificateURLField(source="uuid")

    # This field is not part of the Model, so we add it here to use in the create step.
    # it is write_only so that we do not attempt to show it in the API response.
    lms_user_id = serializers.CharField(write_only=True, required=False)

    def validate_attributes(self, value):
        """Check that the name attributes cannot be duplicated."""
        names = [attribute["name"] for attribute in value]

        if len(names) != len(set(names)):
            raise ValidationError("Attribute names cannot be duplicated.")

        return value

    def issue_credential(self, validated_data):
        """
        Issue a new credential.

        Args:
            validated_data (dict): Input data specifying the credential type, recipient, and attributes.

        Returns:
            AbstractCredential
        """
        accreditor = Accreditor()
        credential = validated_data["credential"]
        username = validated_data["username"]
        status = validated_data.get("status", UserCredentialStatus.AWARDED)
        attributes = validated_data.pop("attributes", None)
        date_override = validated_data.pop("date_override", None)
        lms_user_id = validated_data.pop("lms_user_id", None)
        request = self.context.get("request")
        return accreditor.issue_credential(
            credential,
            username,
            status=status,
            attributes=attributes,
            date_override=date_override,
            request=request,
            lms_user_id=lms_user_id,
        )

    def create(self, validated_data):
        return self.issue_credential(validated_data)

    class Meta:
        model = UserCredential
        fields = UserCredentialSerializer.Meta.fields + ("lms_user_id",)
        read_only_fields = (
            "download_url",
            "uuid",
            "created",
            "modified",
        )


class UserGradeSerializer(serializers.ModelSerializer):
    """Serializer for UserGrade objects."""

    course_run = CourseRunField()

    class Meta:
        model = UserGrade
        fields = (
            "id",
            "username",
            "course_run",
            "letter_grade",
            "percent_grade",
            "verified",
            "lms_last_updated_at",
            "created",
            "modified",
        )
        read_only_fields = (
            "id",
            "created",
            "modified",
        )
        # turn off validation, it only tries to complain about unique_together when updating existing objects
        validators = []

    def is_valid(self, *, raise_exception=False):
        # The LMS sometimes gives us None for the letter grade for some reason. But since the model doesn't take null,
        # just convert it into an empty string instead.
        if self.initial_data.get("letter_grade", "") is None:
            self.initial_data["letter_grade"] = ""

        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):
        # If these next two are missing, the serializer will have already caught the error
        username = validated_data.get("username")
        course_run = validated_data.get("course_run")

        # Support updating or creating when posting to a grade endpoint, since clients don't necessarily know the
        # resource ID to use and we don't need to make them care.
        grade, _ = UserGrade.objects.update_or_create(
            username=username,
            course_run=course_run,
            defaults=validated_data,
        )
        return grade


class SignatorySerializer(serializers.ModelSerializer):
    """Serializer for Signatory objects."""

    organization = serializers.CharField(
        max_length=255, source="organization_name_override", required=False, allow_blank=True
    )

    class Meta:
        model = Signatory
        fields = (
            "image",
            "name",
            "title",
            "organization",
        )

    def validate_image(self, value):
        if value:
            extension = Path(value.name).suffix[1:].lower()
            if extension != "png":
                raise ValidationError("Only PNG files can be uploaded. Please select a file ending in .png to upload.")
        return value


class SignatoryListField(serializers.ListField):
    """
    Serializes a list of strings into a list of dicts.

    Populate signatories images in dict files instead of strings with their filenames.
    """

    def to_internal_value(self, data: str) -> Dict[str, Union[str, InMemoryUploadedFile]]:
        """
        Converts a list of dict that is a string to a list of dict.
        """
        data_ = self.populate_signatories(data, self.context["request"].FILES)  # pylint: disable=no-member
        return super().to_internal_value(data_)

    @staticmethod
    def populate_signatories(
        signatories_data: List[str],
        files: MultiValueDict,
    ) -> Generator[Dict[str, Union[str, InMemoryUploadedFile]], None, None]:
        """
        Populates a list of signature data with files.
        """
        for signatory_data in signatories_data:
            signatory = ast.literal_eval(signatory_data)
            if signatory_file := files.get(signatory.get("image"), None):
                signatory["image"] = signatory_file
                yield signatory

    def to_representation(self, data):
        return super().to_representation(data.all())


class CourseCertificateSerializer(serializers.ModelSerializer):
    course_run = CourseRunField(read_only=True)
    certificate_available_date = serializers.DateTimeField(required=False, allow_null=True)
    signatories = SignatoryListField(child=SignatorySerializer(), required=False)
    title = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = CourseCertificate
        fields = (
            "id",
            "site",
            "course_id",
            "course_run",
            "certificate_type",
            "certificate_available_date",
            "is_active",
            "signatories",
            "title",
        )
        read_only_fields = ("id", "course_run", "site")

    def create(self, validated_data) -> CourseCertificate:
        site = self.context["request"].site
        # A course run may not exist, but if it does, we want to find it. There may be times where course
        # staff will change the date on a newly created course before credentials has pulled it from the catalog.
        course_id = validated_data["course_id"]
        course_run = None
        try:
            course_run = CourseRun.objects.get(key=course_id)
        except ObjectDoesNotExist:
            logger.warning(
                "Course run certificate failed to create "
                f"because the course run [{course_id}] doesn't exist in the catalog"
            )
        # Check if the cert already exists, attempt to update the course_run and cert date
        cert, _ = CourseCertificate.objects.update_or_create(
            course_id=course_id,
            site=site,
            certificate_type=validated_data["certificate_type"],
            defaults={
                "is_active": validated_data["is_active"],
                "course_run": course_run,
                "certificate_available_date": validated_data.get("certificate_available_date"),
                "title": validated_data.get("title"),
            },
        )

        cert.signatories.clear()
        for signatory_data in validated_data.get("signatories", []):
            signatory = Signatory.objects.create(**signatory_data)
            cert.signatories.add(signatory)

        return cert
