from enum import Enum

from ..settings import vc_settings


class StorageType(Enum):
    MOBILE = "mobile"
    WEB = "web"


class BaseWallet:
    """Base Class for Verifiable Credentials wallets.
    This class provides a blueprint for implementing wallet for Verifiable Credentials.
    """

    TYPE = ""
    DEEP_LINK_URL = ""
    ISSUANCE_REQUEST_SERIALIZER = vc_settings.DEFAULT_ISSUANCE_REQUEST_SERIALIZER
    PREFERRED_DATA_MODEL = vc_settings.DEFAULT_DATA_MODELS[0]

    @classmethod
    def get_deeplink_url(cls, issuance_uuid):  # pylint: disable=unused-argument
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
