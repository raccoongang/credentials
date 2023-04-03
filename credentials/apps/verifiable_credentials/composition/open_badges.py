"""
Open Badges 3.0.* data model.
See specification: https://1edtech.github.io/openbadges-specification/ob_v3p0.html
"""

from django.utils.translation import gettext as _
from rest_framework import serializers

from ..composition.status_list import CredentialWithStatusList2021DataModel


class AchievementSchema(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Open Badges achievement.

    https://1edtech.github.io/openbadges-specification/ob_v3p0.html#achievement-0
    """

    TYPE = "Achievement"

    id = serializers.CharField(source="user_credential.uuid")
    type = serializers.CharField(default=TYPE)
    name = serializers.CharField(source="user_credential.credential.title")
    description = serializers.SerializerMethodField(source="user_credential.credential.program.title")

    class Meta:
        read_only_fields = "__all__"

    def get_description(self, issuance_line):
        return (
            issuance_line.user_credential.attributes.filter(name="description").values_list("value", flat=True).first()
        )


class CredentialSubjectSchema(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Open Badges credential subject.
    """

    TYPE = "AchievementSubject"

    id = serializers.CharField(source="subject_id")
    type = serializers.CharField(default=TYPE)
    achievement = AchievementSchema(source="*")

    class Meta:
        read_only_fields = "__all__"


class OpenBadgesDataModel(CredentialWithStatusList2021DataModel):  # pylint: disable=abstract-method
    """
    Open Badges data model.
    """

    VERSION = "3.0"
    ID = "obv3"
    NAME = _("Open Badges Specification v3.0")

    id = serializers.UUIDField(
        source="uuid", format="urn", help_text="https://www.w3.org/TR/vc-data-model/#identifiers"
    )
    name = serializers.CharField(source="credential_name")
    credentialSubject = CredentialSubjectSchema(
        source="*", help_text="https://1edtech.github.io/openbadges-specification/ob_v3p0.html#credentialsubject-0"
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


class OpenBadges301DataModel(OpenBadgesDataModel):  # pylint: disable=abstract-method
    """
    Open Badges data model.
    """

    VERSION = "3.0.1"
    ID = "obv301"
    NAME = _("Open Badges Specification v3.0.1")

    @classmethod
    def get_context(cls):
        return [
            "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.1.json",
            "https://purl.imsglobal.org/spec/ob/v3p0/extensions.json",
        ]
