"""
Verifiable Credentials v1.1 data model.

See specification: https://www.w3.org/TR/vc-data-model/
"""
from enum import Enum

from django.utils.translation import gettext as _
from rest_framework import serializers

from ..composition import CredentialDataModel


class SubjectDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="subject_id", read_only=True)
    name = serializers.CharField(required=False, read_only=True)


class VerifiableCredentialsDataModel(CredentialDataModel):  # pylint: disable=abstract-method
    """
    Verifiable Credentials data model.
    """

    VERSION = 1.1
    ID = "vc"
    NAME = _("Verifiable Credentials Data Model v1.1")

    issuer = serializers.CharField(source="issuer_id")
    issuanceDate = serializers.DateTimeField(source="modified")
    credentialSubject = serializers.SerializerMethodField(method_name="get_subject")

    class Meta:
        read_only_fields = "__all__"

    def get_subject(self, issuance_line):
        return SubjectDataModel(issuance_line).data
