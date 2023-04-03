"""
Verifiable credentials specific permissions.
"""
from rest_framework.permissions import BasePermission


class VerifiablePresentation(BasePermission):
    """
    Allow based on provided verifiable credential.
    """

    def has_permission(self, request, view):
        """
        If a verifiable presentation with a proofPurpose "authentication" provided - validate it and decide.

        FIXME: validate with didkit
        {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1"
            ],
            "type": [
                "VerifiablePresentation"
            ],
            "holder": "<issuer-did>",
            "proof": {
                "type": "Ed25519Signature2020",
                "created": "2023-04-03T13:18:05Z",
                "verificationMethod": "<issuer-did>",
                "proofPurpose": "authentication",
                "challenge": "c44c45c6-e6e1-4db1-ac2d-413aa0eaf438",
                "proofValue": "z5B2bRwmvzoAfJ8JnsnnXCdAMBk28nW9NY8eVm83HSq92MkA8rCq2SVx58pwYiTzZFQNb2hHt3NEc1DQ..."
            }
        }
        """

        try:
            if "VerifiablePresentation" in request.data["type"]:
                return True
        except (KeyError, TypeError, IndexError):
            pass
        return False
