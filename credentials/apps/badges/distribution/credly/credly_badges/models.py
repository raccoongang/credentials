"""
Credly Badges DB models.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from credentials.apps.credentials.models import UserCredential
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from model_utils.fields import StatusField

from credentials.apps.badges.models import BadgeTemplate


class CredlyOrganization(TimeStampedModel):
    """
    Credly Organization configuration.
    """

    uuid = models.UUIDField(unique=True, help_text=_("Put your Credly Organization ID here."))
    api_key = models.CharField(max_length=255, help_text=_("Credly API shared secret for Credly Organization."))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Verbose name for Credly Organization."))

    def __str__(self):
        return f"{self.name or self.uuid}"

    @classmethod
    def get_all_organization_ids(cls):
        """
        Get all organization IDs.
        """
        return cls.objects.values_list("uuid", flat=True)


class CredlyBadgeTemplate(BadgeTemplate):
    """
    Credly badge template.
    """

    TYPE = "credly"
    STATES = Choices("draft", "active", "archived")

    organization = models.ForeignKey(
        CredlyOrganization,
        on_delete=models.CASCADE,
        help_text=_("Credly Organization - template owner."),
    )
    state = StatusField(
        choices_name="STATES",
        help_text=_("Credly badge template state (auto-managed)."),
    )


class CredlyBadge(UserCredential):
    """
    Earned Credly badge template for user.
    """
    # TODO: check if we can fetch pii for username from LMS for badge issuing?

    ISSUING_STATES = Choices("created", "no_response", "error", "pending", "accepted", "rejected", "revoked")

    issuing_state = StatusField(
        choices_name="ISSUING_STATES",
        help_text=_("Credly badge issuing state"),
        default=ISSUING_STATES.created,
    )
    recipient_email = models.EmailField()
    issued_to_first_name = models.CharField(max_length=30)
    issued_to_last_name = models.CharField(max_length=150)
    issued_at = models.DateTimeField(auto_now_add=True)

    badge_template_id = models.PositiveIntegerField()
