"""
Open Badges 3.0 data model.

See specification: https://1edtech.github.io/openbadges-specification/ob_v3p0.html
"""
from ..composition import BaseDataModel


class OpenBadgesDataModel(BaseDataModel):
    """
    Open Badges data model.
    """
    VERSION = 3.0

    def to_representation(self, instance):
        return {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
                "https://purl.imsglobal.org/spec/ob/v3p0/context.json"
            ],
            "id": "http://example.edu/credentials/3732",
            "type": ["VerifiableCredential", "OpenBadgeCredential"],
            "issuer": {
                "id": "https://example.edu/issuers/565049",
                "type": ["IssuerProfile"],
                "name": "Example University"
            },
            "issuanceDate": "2010-01-01T00:00:00Z",
            "name": "Teamwork Badge",
            "credentialSubject": {
                "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
                "type": ["AchievementSubject"],
                "achievement": {
                    "id": "https://example.com/achievements/21st-century-skills/teamwork",
                    "type": [
                        "Achievement"
                    ],
                    "criteria": {
                        "narrative": "Team members are nominated for this badge by their peers and recognized upon review by Example Corp management."
                    },
                    "description": "This badge recognizes the development of the capacity to collaborate within a group environment.",
                    "name": "Teamwork"
                }
            }
        }
