"""
Verifiable Credentials v1.1 data model.

See specification: https://www.w3.org/TR/vc-data-model/
"""
from enum import Enum

from django.utils.translation import gettext as _
from rest_framework import serializers

from ..composition import CredentialDataModel


class SubjectSchema(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="subject_id")

    class Meta:
        read_only_fields = "__all__"


class VerifiableCredentialsDataModel(CredentialDataModel):  # pylint: disable=abstract-method
    """
    Verifiable Credentials data model.
    """

    VERSION = 1.1
    ID = "vc"
    NAME = _("Verifiable Credentials Data Model v1.1")

    context = serializers.SerializerMethodField(
        method_name="collect_context", help_text="https://www.w3.org/TR/vc-data-model/#contexts"
    )
    id = serializers.UUIDField(
        source="uuid", format="urn", help_text="https://www.w3.org/TR/vc-data-model/#identifiers"
    )
    type = serializers.SerializerMethodField(help_text="https://www.w3.org/TR/vc-data-model/#types")
    issuer = serializers.CharField(source="issuer_id", help_text="https://www.w3.org/TR/vc-data-model/#issuer")
    issued = serializers.DateTimeField(source="modified", help_text="https://www.w3.org/2018/credentials/#issued")
    issuanceDate = serializers.DateTimeField(
        source="modified",
        help_text="Deprecated (requred by the didkit for now) https://www.w3.org/2018/credentials/#issuanceDate",
    )
    validFrom = serializers.DateTimeField(source="modified", help_text="https://www.w3.org/2018/credentials/#validFrom")
    validUntil = serializers.DateTimeField(
        source="expiration_date", help_text="https://www.w3.org/2018/credentials/#validUntil"
    )
    credentialSubject = SubjectSchema(source="*", help_text="https://www.w3.org/2018/credentials/#credentialSubject")

    class Meta:
        read_only_fields = "__all__"

    @classmethod
    def get_context(cls):
        """
        Provide root context for all verifiable credentials.
        """
        return [
            "https://www.w3.org/2018/credentials/v1",
        ]

    @classmethod
    def get_types(cls):
        """
        Provide root types for all verifiable credentials.
        """
        return [
            "VerifiableCredential",
        ]
