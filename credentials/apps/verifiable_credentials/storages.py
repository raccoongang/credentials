from enum import Enum
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from .settings import vc_settings


class StorageType(Enum):
    MOBILE = "mobile"
    WEB = "web"


class BaseWallet:
    """Base Class for Verifiable Credentials wallets.
    This class provides a blueprint for implementing wallet for Verifiable Credentials.
    """

    DEEP_LINK_URL = ""
    ISSUANCE_REQUEST_SERIALIZER = vc_settings.DEFAULT_ISSUANCE_REQUEST_SERIALIZER

    @classmethod
    def get_deeplink_url(cls, *args, **kwargs):
        return cls.DEEP_LINK_URL

    @classmethod
    def is_mobile(cls):
        return cls.TYPE == StorageType.MOBILE

    @classmethod
    def is_web(cls):
        return cls.TYPE == StorageType.WEB


class MobileWallet(BaseWallet):
    TYPE = StorageType.MOBILE
    APP_LINK_ANDROID = ""
    APP_LINK_IOS = ""


class WebWallet(BaseWallet):
    TYPE = StorageType.WEB


class LCWallet(MobileWallet):
    """
    Learner Credential Wallet by DCC.
    """

    ID = "lcwallet"
    APP_LINK_ANDROID = "https://play.google.com/store/apps/details?id=app.lcw"
    APP_LINK_IOS = "https://apps.apple.com/app/learner-credential-wallet/id1590615710"
    DEEP_LINK_URL = "dccrequest://request"

    @classmethod
    def get_deeplink_url(cls, issuance_uuid):
        params = {
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
