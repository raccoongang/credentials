"""
This module provides classes for issuing badge credentials to users.
"""

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from credentials.apps.badges.models import BadgeTemplate, CredlyBadge, CredlyBadgeTemplate, UserCredential
from credentials.apps.credentials.constants import UserCredentialStatus
from credentials.apps.credentials.issuers import AbstractCredentialIssuer

from .awarding import notify_badge_awarded
from .revocation import notify_badge_revoked


class BadgeTemplateIssuer(AbstractCredentialIssuer):
    """
    Issues BadgeTemplate credentials to users.
    """

    issued_credential_type = BadgeTemplate
    issued_user_credential_type = UserCredential

    def get_credential(self, credential_id):
        return self.issued_credential_type.objects.get(id=credential_id)

    @transaction.atomic
    def issue_credential(
        self,
        credential,
        username,
        status=UserCredentialStatus.AWARDED,
        attributes=None,
        date_override=None,
        request=None,
        lms_user_id=None,  # pylint: disable=unused-argument
    ):
        """
        Issue a credential to the user.

        This action is idempotent. If the user has already earned the credential, a new one WILL NOT be issued. The
        existing credential WILL be modified.

        Arguments:
            credential (AbstractCredential): Type of credential to issue.
            username (str): username of user for which credential required
            status (str): status of credential
            attributes (List[dict]): optional list of attributes that should be associated with the issued credential.
            request (HttpRequest): request object to build program record absolute uris

        Returns:
            UserCredential
        """

        user_credential, __ = self.issued_user_credential_type.objects.update_or_create(
            username=username,
            credential_content_type=ContentType.objects.get_for_model(credential),
            credential_id=credential.id,
            defaults={
                "status": status,
            },
        )

        self.set_credential_attributes(user_credential, attributes)
        self.set_credential_date_override(user_credential, date_override)

        return user_credential

    def award(self, credential_id, username):
        credential = self.get_credential(credential_id)
        user_credential = self.issue_credential(credential, username)

        notify_badge_awarded(user_credential)
        return user_credential

    def revoke(self, credential_id, username):
        credential = self.get_credential(credential_id)
        user_credential = self.issue_credential(credential, username, status=UserCredentialStatus.REVOKED)

        notify_badge_revoked(user_credential)
        return user_credential


class CredlyBadgeTemplateIssuer(BadgeTemplateIssuer):
    """
    Issues CredlyBadgeTemplate credentials to users.
    """

    issued_credential_type = CredlyBadgeTemplate
    issued_user_credential_type = CredlyBadge
