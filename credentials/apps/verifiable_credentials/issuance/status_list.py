"""
Status List issuance utils.

Status list is managed for each Issuer separately.
Status lists are verifiable credentials themselves, but with a specific shape.
"""
import base64
import gzip
import logging

from django.utils.translation import gettext as _

from ..issuance.main import CredentialIssuer
from ..settings import vc_settings
from . import IssuanceException
from .models import get_registered_issuers, get_revoked_indices


logger = logging.getLogger(__name__)


# def make_status_list_path(issuer_did):
#     return f"{settings.ROOT_URL}{vc_settings.STATUS_LIST['PUBLIC_PATH']}{issuer_did}.json"


def issue_status_lists():
    """
    Initiate Status List 2021 for each Issuer.

    "Status List 2021" is a special kind of a verifiable credential.
    """
    for issuer_dict in get_registered_issuers():
        issuance_line = CredentialIssuer.init(
            storage_id=vc_settings.STATUS_LIST_STORAGE.ID, issuer_id=issuer_dict["issuer_id"]
        )
        credential_issuer = CredentialIssuer(issuance_uuid=issuance_line.uuid, data=issuer_dict)
        try:
            status_list = credential_issuer.issue()
            print(status_list)
        except IssuanceException:
            msg = _("Status List generation failed: [{issuer_id}]").format(issuer_id=issuance_line.issuer_id)
            logger.exception(msg)


def regenerate_encoded_status_sequence(issuer_id):
    """
    Create Status List indecies sequence from scratch for given Issuer.
    """
    status_list = bytearray(vc_settings.STATUS_LIST_LENGTH)

    for index in get_revoked_indices(issuer_id):
        status_list[index] = 1

    gzip_data = gzip.compress(status_list)
    base64_data = base64.b64encode(gzip_data)
    return base64_data.decode("utf-8")
