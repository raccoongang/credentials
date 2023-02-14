from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.urls import reverse


class BaseWallet:
    """Base Class for Verifiable Credentials wallets.
    This class provides a blueprint for implementing wallet for Verifiable Credentials.
    """

    APP_LINK_ANDROID = "SET-ME-PLEASE"
    APP_LINK_IOS = "SET-ME-PLEASE"

    @classmethod
    def create_deeplink_url(cls, issuance_uuid):
        """Create a deeplink URL.
        Args:
            issuance_uuid (str): Unique identifier for the VerifiableCredentialIssuance.
        Returns:
            str: Deeplink URL.
        """
        raise NotImplementedError

    @classmethod
    def create_qr_code(cls, issuance_uuid):
        """Create a QR code for a credential.
        Args:
            issuance_uuid (str): Unique identifier for the VerifiableCredentialIssuance.
        Returns:
            str: QR code data.
        """
        raise NotImplementedError


class LCWallet(BaseWallet):
    AUTH_TYPE = "code"
    DEEP_LINK_URL = "dccrequest://request"
    APP_LINK_ANDROID = "https://play.google.com/store/apps/details?id=app.lcw"
    APP_LINK_IOS = "https://apps.apple.com/app/learner-credential-wallet/id1590615710"

    @classmethod
    def create_deeplink_url(cls, issuance_uuid):
        params = {
            "auth_type": cls.AUTH_TYPE,
            "issuer": settings.ROOT_URL,
            "vc_request_url": urljoin(
                settings.ROOT_URL,
                reverse(
                    "verifiable_credentials:api:v1:credentials-issue",
                    kwargs={"issuance_uuid": issuance_uuid.hex},
                ),
            ),
            "challenge": issuance_uuid.hex,
        }

        return f"{cls.DEEP_LINK_URL}?{urlencode(params)}"

    @classmethod
    def create_qr_code(cls, issuance_uuid):
        return "qrcode"
