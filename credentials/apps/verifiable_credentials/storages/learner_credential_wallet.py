from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _

from ..composition.open_badges import OpenBadgesDataModel
from ..issuance.models import IssuanceLine
from ..issuance.serializers import IssuanceLineSerializer
from ..storages import MobileWallet


# FIXME - review this
class LearnerCredentialWalletRequest(IssuanceLineSerializer):
    """
    Specific storage adapter.

    Another storage may not provide expected shape for issuance request (field names, structure).
    """

    def to_internal_value(self, data):
        """
        Maps storage-specific request properties to the unified verifiable credential source data.
        """
        self.swap_value(data, "holder", "subject_id")
        return super().to_internal_value(data)


class LCWallet(MobileWallet):
    """
    Learner Credential Wallet by DCC.
    """

    ID = "lc_wallet"
    NAME = _("Learner Credential Wallet")
    APP_LINK_ANDROID = "https://play.google.com/store/apps/details?id=app.lcw"
    APP_LINK_IOS = "https://apps.apple.com/app/learner-credential-wallet/id1590615710"
    DEEP_LINK_URL = "dccrequest://request"
    ISSUANCE_REQUEST_SERIALIZER = LearnerCredentialWalletRequest
    PREFERRED_DATA_MODEL = OpenBadgesDataModel

    @classmethod
    def get_deeplink_url(cls, issuance_uuid, **kwargs):
        params = {
            "issuer": IssuanceLine.objects.get(uuid=issuance_uuid).issuer_id,
            "vc_request_url": urljoin(
                settings.ROOT_URL,  # FIXME provide context from view / crum
                reverse(
                    "verifiable_credentials:api:v1:credentials-issue",
                    kwargs={"issuance_line_uuid": issuance_uuid},
                ),
            ),
            "challenge": issuance_uuid,
            "auth_type": "bearer"
        }
        return f"{cls.DEEP_LINK_URL}?{urlencode(params)}"

    @classmethod
    def prepare_response(cls, composed_credential_json, **kwargs):
        return composed_credential_json
