"""
Digital credentials formats.
"""
from datetime import datetime
from urllib.parse import urljoin

import pytz
from django.conf import settings

from credentials.apps.credentials.models import ProgramCertificate

from .exceptions import UnexpectedCredentialTypeException
from .models import VerifiableCredentialIssuance


def compose_verifiable_credential(data):  # pylint: disable=unused-argument
    """
    Compose "Verifiable Credential v1.1" digital credential.
    """


def compose_open_badge_v3(data):
    """
    Compose "Open Badges v3" digital credential.
    """

    def _build_program_achievement(user_credential):
        return {
            "id": urljoin(settings.ROOT_URL, user_credential.download_url),
            "type": ["Achievement"],
            "name": user_credential.credential.program.title,
        }

    challenge = data["proof"]["challenge"]

    issuance = VerifiableCredentialIssuance.objects.get(uuid=challenge)
    user_credential = issuance.user_credential

    if isinstance(user_credential.credential, ProgramCertificate):
        achievement = _build_program_achievement(user_credential)
    else:
        raise UnexpectedCredentialTypeException(
            f"Unexpected courseware object type for digital credentials: {type(user_credential)}"
        )

    return {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://purl.imsglobal.org/spec/ob/v3p0/context/ob_v3p0.jsonld",
        ],
        "id": urljoin(settings.ROOT_URL, issuance.user_credential.download_url),
        "type": ["VerifiableCredential", "OpenBadgeCredential"],
        "issuanceDate": datetime.now(tz=pytz.UTC).isoformat(),
        "issuer": settings.ROOT_URL,
        "credentialSubject": {
            # FIXME
            "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
            "type": "AchievementSubject",
            "achievement": achievement,
        },
    }
