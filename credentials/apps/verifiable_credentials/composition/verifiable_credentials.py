"""
Verifiable Credentials v1.1 data model.

See specification: https://www.w3.org/TR/vc-data-model/
"""
from enum import Enum

from django.utils.translation import gettext as _
from rest_framework import serializers

from ..composition import BaseDataModel


class Types(Enum):
    VERIFIABLE_CREDENTIAL = "VerifiableCredential"
    UNIVERSITY_DEGREE_CREDENTIAL = "UniversityDegreeCredential"


class SubjectDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="subject_id", read_only=True)
    name = serializers.CharField(required=False, read_only=True)


class VerifiableCredentialsDataModel(BaseDataModel):  # pylint: disable=abstract-method
    """
    Verifiable Credentials data model.
    """

    VERSION = 1.1
    ID = "vc"
    NAME = _("Verifiable Credentials Data Model v1.1")

    type = serializers.SerializerMethodField()
    issuer = serializers.CharField(source="issuer_id", read_only=True)
    issuanceDate = serializers.DateTimeField(source="modified", read_only=True)
    credentialSubject = serializers.SerializerMethodField(method_name="get_subject")

    @property
    def context(self):
        return [
            "https://www.w3.org/2018/credentials/v1",
            "https://www.w3.org/2018/credentials/examples/v1",
        ]

    def get_type(self, issuance_line):
        default_types = [Types.VERIFIABLE_CREDENTIAL.value]
        credential_content_type = issuance_line.user_credential.credential_content_type.model
        return default_types + self.map_credential_types(credential_content_type)

    def get_subject(self, issuance_line):
        return SubjectDataModel(issuance_line).data

    @staticmethod
    def map_credential_types(content_type):
        """
        Maps Open edX credential type to data model types/
        """
        linked_types = {
            "programcertificate": [
                Types.UNIVERSITY_DEGREE_CREDENTIAL.value,  # FIXME: as example
            ],
            "coursecertificate": [],
        }

        if content_type not in linked_types:
            return []

        return linked_types[content_type]
