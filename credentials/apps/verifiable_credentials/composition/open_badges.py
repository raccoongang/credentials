"""
Open Badges 3.0 data model.
See specification: https://1edtech.github.io/openbadges-specification/ob_v3p0.html
"""

from django.utils.translation import gettext as _
from rest_framework import serializers

from ..composition import CredentialDataModel


class CredentialSubjectSchema(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="subject_id")
    # hasCredential = EducationalOccupationalCredentialSchema(source="*")

    class Meta:
        read_only_fields = "__all__"


class OpenBadgesDataModel(CredentialDataModel):  # pylint: disable=abstract-method
    """
    Open Badges data model.
    """

    VERSION = 3.0
    ID = "obv3"
    NAME = _("Open Badges Specification v3.0")

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
        return [
            "https://purl.imsglobal.org/spec/ob/v3p0/context.json",
        ]

    @classmethod
    def get_types(cls):
        return [
            "OpenBadgeCredential",
        ]
