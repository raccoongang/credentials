"""
Verifiable Credentials v1.1 data model.

See specification: https://www.w3.org/TR/vc-data-model/
"""
from django.utils.translation import gettext as _
from rest_framework import serializers

from . import CredentialDataModel
from .schemas import CredentialSubjectSchema
from .status_list import StatusList2021EntryMixin


class VerifiableCredentialsDataModel(StatusList2021EntryMixin, CredentialDataModel):  # pylint: disable=abstract-method
    """
    Verifiable Credentials data model.
    """

    VERSION = 1.1
    ID = "vc"
    NAME = _("Verifiable Credentials Data Model v1.1")

    id = serializers.UUIDField(
        source="uuid", format="urn", help_text="https://www.w3.org/TR/vc-data-model/#identifiers"
    )
    credentialSubject = CredentialSubjectSchema(
        source="*", help_text="https://www.w3.org/2018/credentials/#credentialSubject"
    )

    class Meta:
        read_only_fields = "__all__"

    @classmethod
    def get_context(cls):
        """
        Provide root context for all verifiable credentials.
        """
        return [
            "https://schema.org/",
        ]
