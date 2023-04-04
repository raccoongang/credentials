import didkit
from asgiref.sync import async_to_sync


@async_to_sync
async def didkit_issue_credential(credential, options, issuer_key):
    return await didkit.issue_credential(credential, options, issuer_key)  # pylint: disable=no-member


@async_to_sync
async def didkit_verify_credential(credential, proof_options):
    return await didkit.verify_credential(credential, proof_options)  # pylint: disable=no-member


@async_to_sync
async def didkit_verify_presentation(presentation, proof_options):
    return await didkit.verify_presentation(presentation, proof_options)  # pylint: disable=no-member



class IssuanceException(Exception):
    """
    Outlines a general error during a verifiable credential issuance.
    """

    def __init__(self, detail=None):
        self.detail = detail

    def __str__(self):
        return str(self.detail)
