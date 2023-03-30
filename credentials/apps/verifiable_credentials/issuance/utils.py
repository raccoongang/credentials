"""
Issuance utils.
"""
# pylint: disable=cyclic-import
from django.utils.translation import gettext as _

from credentials.apps.credentials.models import UserCredential

from ..settings import VerifiableCredentialsImproperlyConfigured
from .models import IssuanceConfiguration, IssuanceLine


def create_issuers():
    """
    Initiate issuers.
    """
    return IssuanceConfiguration.create_issuers()


def get_active_issuers():
    """
    Collect all enabled issuers' ids.
    """
    # currently, the only (system level, default) is supported.
    return list(IssuanceConfiguration.objects.filter(enabled=True).values_list("issuer_id", flat=True))


def get_issuers():
    """
    Collect all issuers.
    """
    # currently, the only (system level, default) is supported.
    return list(IssuanceConfiguration.objects.values())


def get_issuer_ids():
    """
    Collect all issuers' ids.
    """
    # currently, the only (system level, default) is supported.
    return list(IssuanceConfiguration.objects.values_list("issuer_id", flat=True))


def get_default_issuer():
    """
    Fetch the default issuer.
    """
    issuer = IssuanceConfiguration.objects.filter(enabled=True).last()
    if not issuer:
        msg = _("There are no enabled Issuance Configurations for some reason! At least one must be always active.")
        raise VerifiableCredentialsImproperlyConfigured(msg)
    return issuer


def get_issuer(issuer_id):
    """
    Fetch issuer by given ID.
    """
    issuer = IssuanceConfiguration.objects.filter(issuer_id=issuer_id).first()
    return issuer


def get_revoked_indices(issuer_id):
    """
    Collect status indicies for verifiable credentials with revoked achievements (in given Issuer context).
    """
    return IssuanceLine.get_indicies_for_status(issuer_id=issuer_id, status=UserCredential.REVOKED)
