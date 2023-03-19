"""
Open Badges 3.0 data model.
See specification: https://1edtech.github.io/openbadges-specification/ob_v3p0.html
"""

from django.utils.translation import gettext as _

from ..composition.verifiable_credentials import VerifiableCredentialsDataModel


class OpenBadgesDataModel(VerifiableCredentialsDataModel):  # pylint: disable=abstract-method
    """
    Open Badges data model.
    """

    VERSION = 3.0
    ID = "obv3"
    NAME = _("Open Badges Specification v3.0")

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
