"""
SpruceID DIDKit based issuance.
See: https://www.spruceid.dev/didkit/didkit-packages/python
"""

from .composition import open_badge_v3, verifiable_credential
from ..constants import OPEN_BADGES_V3_KEY, VERIFIABLE_CREDENTIAL_KEY


class DIDKitIssuer:
    """
    Issuer is responsible for digital credential composition and signing.

    - key auto-generation vs improperly configured?
    - DID auto-generation vs improperly configured?
    - VC expiration?
    """

    formats = {
        VERIFIABLE_CREDENTIAL_KEY: verifiable_credential,
        OPEN_BADGES_V3_KEY: open_badge_v3,
    }

    # TODO: try to use `attrs` lib.
    def __init__(self, *, params=None, options=None):
        self._request = params or {}
        self._options = options or {}
        self._config = {}

    def compose(self):
        """
        Build a digital credential document for signing.
        """
        self._get_format()
        pass

    def issue_credential(self):
        """
        Create signed digital credential document.
        """
        # didkit.issue_credential()
        pass

    def _get_format(self):
        """
        Choose an appropriate document format to build.
        """
        # get pick from self.formats based on the current config

    def _get_issuance_config(self):
        """
        Load appropriate issuance configuration.
        """
        # use Org/Site or system defaults
        # add DID to Org/Site config
        # add key to Org/Site config
        pass

    def _load_keys(self):
        """
        Pick signing key(s).
        """
        pass
