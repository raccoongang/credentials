"""
Verifiable Credentials v1.1 data model.

See specification: https://www.w3.org/TR/vc-data-model/
"""
from ..composition import BaseDataModel


class VerifiableCredentialsDataModel(BaseDataModel):
    """
    Verifiable Credentials data model.
    """
    VERSION = 1.1

    def to_representation(self, instance):
        return {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1"
            ],
            "id": "http://example.edu/credentials/3732",
            "type": [
                "VerifiableCredential",
                "UniversityDegreeCredential"
            ],
            "issuer": "https://example.edu/issuers/565049",
            "issuanceDate": "2010-01-01T00:00:00Z",
            "credentialSubject": {
                "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
                "degree": {
                    "type": "BachelorDegree",
                    "name": "Bachelor of Science and Arts"
                }
            }, }
