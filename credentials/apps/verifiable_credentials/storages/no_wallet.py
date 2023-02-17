"""
NOTE: this module initially was supposed to be extracted to installable plugin.
"""
from urllib.parse import urlencode

from django.urls import reverse

from credentials.apps.verifiable_credentials.storages import WebWallet


class NoWallet(WebWallet):
    """
    Credentials internal storage backend for local verifiable credentials download.

    No external wallet/vault is connected. This storage redirects to a simple internal page
    with a form to:
    - provide additional issuance properties (e.g. holder DID)
        - option: choose data model to use
        - option: explicitly separate holder/subject
    - submit issuance form
    - render returned verifiable credential (visualization)
    - download returned verifiable credential as a JSON file
        - option: other formats

    This storage backend is planned as a separate installable Open edX Credentials plugin.
    Once it is installed and added to VERIFIABLE_CREDENTIALS = {DEFAULT_STORAGES: []} settings it is activated -
    additional "Download" button should be available in the Learner Record MFE UI.
    """

    ID = "nowallet"
    DEEP_LINK_URL = reverse("verifiable_credentials:api:v1:credentials-nowallet")

    @classmethod
    def get_deeplink_url(cls, issuance_uuid):
        params = {
            "issuance_url": reverse(
                "verifiable_credentials:api:v1:credentials-issue",
                kwargs={"issuance_uuid": issuance_uuid.hex},
            ),
            "challenge": issuance_uuid.hex,
        }
        return f"{cls.DEEP_LINK_URL}?{urlencode(params)}"
