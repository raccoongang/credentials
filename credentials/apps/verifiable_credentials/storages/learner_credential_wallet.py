from urllib.parse import urlencode, urljoin

from crum import get_current_request
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _

from ..composition.verifiable_credentials import VerifiableCredentialsDataModel

from ..composition.open_badges import OpenBadgesDataModel
from ..issuance.serializers import IssuanceLineSerializer
from ..storages import MobileWallet


class LCWallet(MobileWallet):
    """
    Learner Credential Wallet by DCC.
    """

    ID = "lc_wallet"
    NAME = _("Learner Credential Wallet")

    APP_LINK_ANDROID = "https://play.google.com/store/apps/details?id=app.lcw"
    APP_LINK_IOS = "https://apps.apple.com/app/learner-credential-wallet/id1590615710"
    DEEP_LINK_URL = "dccrequest://request"

    PREFERRED_DATA_MODEL = OpenBadgesDataModel
    # PREFERRED_DATA_MODEL = VerifiableCredentialsDataModel

    @classmethod
    def get_deeplink_url(cls, issuance_line, **kwargs):
        request = get_current_request()
        if not request:
            return None

        # issuance_base_url = request.build_absolute_uri().split(request.path)[0]
        issuance_base_url = "http://8825-92-118-76-214.ngrok.io/"

        params = {
            "issuer": issuance_line.issuer_id,
            "vc_request_url": urljoin(
                issuance_base_url,
                reverse(
                    "verifiable_credentials:api:v1:credentials-issue",
                    kwargs={"issuance_line_uuid": issuance_line.uuid},
                ),
            ),
            "auth_type": "bearer",
            "challenge": issuance_line.uuid,
        }
        return f"{cls.DEEP_LINK_URL}?{urlencode(params)}"
