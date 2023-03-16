"""
Open Badges 3.0 data model.
See specification: https://1edtech.github.io/openbadges-specification/ob_v3p0.html
"""
from enum import Enum

from django.utils.translation import gettext as _
from rest_framework import serializers

from ..composition import CredentialDataModel


class Types(Enum):
    VERIFIABLE_CREDENTIAL = "VerifiableCredential"
    OPEN_BADGE_CREDENTIAL = "OpenBadgeCredential"
    ISSUER_PROFILE = "IssuerProfile"
    ACHIEVEMENT_SUBJECT = "AchievementSubject"
    ACHIEVEMENT = "Achievement"


class IssuerDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="issuer_id", read_only=True)
    type = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_type(self, *args, **kwargs):
        return [Types.ISSUER_PROFILE.value]

    def get_name(self, *args, **kwargs):
        return "Example University"


class AchievementDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_type(self, *args, **kwargs):
        return [Types.ACHIEVEMENT.value]

    def get_id(self, issuance_line):
        return issuance_line.user_credential.download_url


class SubjectDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.CharField(source="subject_id", read_only=True)
    type = serializers.SerializerMethodField()
    achievement = serializers.SerializerMethodField()

    def get_achievement(self, issuance_line):
        return AchievementDataModel(issuance_line).data

    def get_type(self, *args, **kwargs):
        return [Types.ACHIEVEMENT_SUBJECT.value]


class OpenBadgesDataModel(CredentialDataModel):  # pylint: disable=abstract-method
    """
    Open Badges data model.
    """

    VERSION = 3.0
    ID = "obv3"
    NAME = _("Open Badges Specification v3.0")

    issuer = serializers.SerializerMethodField()
    issuanceDate = serializers.DateTimeField(source="modified")
    name = serializers.SerializerMethodField()
    credentialSubject = serializers.SerializerMethodField(method_name="get_subject")

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

    def get_subject(self, issuance_line):
        return SubjectDataModel(issuance_line).data

    def get_name(self, issuance_line):
        return issuance_line.user_credential.credential_content_type.model

    def get_issuer(self, issuance_line):
        return IssuerDataModel(issuance_line).data
