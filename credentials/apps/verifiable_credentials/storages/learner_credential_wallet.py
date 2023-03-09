from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _

from ..composition.open_badges import OpenBadgesDataModel
from ..serializers import IssuanceLineSerializer
from ..storages import MobileWallet


class LearnerCredentialWalletRequest(IssuanceLineSerializer):
    """
    Specific storage adapter.

    Another storage may not provide expected shape for issuance request (field names, structure).
    """

    def to_internal_value(self, data):
        """
        Maps storage-specific request properties to the unified verifiable credential source data.
        """
        self.swap_value(data, "holder", "holder_id")
        return super().to_internal_value(data)


class LCWallet(MobileWallet):
    """
    Learner Credential Wallet by DCC.
    """

    ID = "lc_wallet"
    VERBOSE_NAME = _("Learner Credential Wallet")
    APP_LINK_ANDROID = "https://play.google.com/store/apps/details?id=app.lcw"
    APP_LINK_IOS = "https://apps.apple.com/app/learner-credential-wallet/id1590615710"
    DEEP_LINK_URL = "dccrequest://request"
    ISSUANCE_REQUEST_SERIALIZER = LearnerCredentialWalletRequest
    PREFERRED_DATA_MODEL = OpenBadgesDataModel

    @classmethod
    def get_deeplink_url(cls, issuance_uuid):
        params = {
            "issuer": settings.ROOT_URL,
            "vc_request_url": urljoin(
                settings.ROOT_URL,
                reverse(
                    "verifiable_credentials:api:v1:credentials-issue",
                    kwargs={"issuance_line_uuid": issuance_uuid},
                ),
            ),
            "challenge": issuance_uuid,
        }
        return f"{cls.DEEP_LINK_URL}?{urlencode(params)}"
