"""
Badges DB models.
"""

import uuid

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from model_utils.fields import StatusField

from credentials.apps.badges.utils import is_datapath_valid
from credentials.apps.credentials.models import AbstractCredential, UserCredential


class CredlyOrganization(TimeStampedModel):
    """
    Credly Organization configuration.
    """

    uuid = models.UUIDField(
        unique=True, help_text=_("Put your Credly Organization ID here.")
    )
    api_key = models.CharField(
        max_length=255, help_text=_("Credly API shared secret for Credly Organization.")
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Verbose name for Credly Organization."),
    )

    def __str__(self):
        return f"{self.name or self.uuid}"

    @classmethod
    def get_all_organization_ids(cls):
        """
        Get all organization IDs.
        """
        return list(cls.objects.values_list("uuid", flat=True))


class BadgeTemplate(AbstractCredential):
    """
    Describes badge credential type.
    """

    ORIGIN = "openedx"

    STATES = Choices("draft", "active", "archived")

    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text=_("Unique badge template ID.")
    )
    name = models.CharField(max_length=255, help_text=_("Badge template name."))
    description = models.TextField(
        null=True, blank=True, help_text=_("Badge template description.")
    )
    icon = models.ImageField(upload_to="badge_templates/icons", null=True, blank=True)
    origin = models.CharField(
        max_length=128, null=True, blank=True, help_text=_("Badge template type.")
    )
    state = StatusField(
        choices_name="STATES",
        help_text=_("Credly badge template state (auto-managed)."),
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save()
        # auto-evaluate type:
        if not self.origin:
            self.origin = self.ORIGIN
            self.save(*args, **kwargs)

    @classmethod
    def by_uuid(cls, template_uuid):
        return cls.objects.filter(uuid=template_uuid, origin=cls.ORIGIN).first()
    
    def user_progress(self, username: str) -> float:
        """
        Calculate user progress for badge template.
        """
        requirements_count = BadgeRequirement.objects.filter(template=self).count()
        if requirements_count == 0:
            raise ValueError("No requirements found for badge template")

        fulfilled_requirements_count = Fulfillment.objects.filter(progress__username=username, requirement__template=self).count()
        return fulfilled_requirements_count / requirements_count
    
    def user_completion(self, username: str) -> bool:
        """
        Check if user completed badge template.
        """
        return self.user_progress(username) == 1.0


class CredlyBadgeTemplate(BadgeTemplate):
    """
    Credly badge template.
    """

    ORIGIN = "credly"

    organization = models.ForeignKey(
        CredlyOrganization,
        on_delete=models.CASCADE,
        help_text=_("Credly Organization - template owner."),
    )

    @property
    def management_url(self):
        """
        Build external Credly dashboard URL.
        """
        credly_host_base_url = "https://sandbox.credly.com"
        return f"{credly_host_base_url}/mgmt/organizations/{self.organization.uuid}/badges/templates/{self.uuid}/details"


class BadgeRequirement(models.Model):
    """
    Describes what must happen and how such event will affect badge progress.

    NOTE:   Badge template's requirements implement "AND" processing logic (e.g. all requirements must be fulfilled).
            To achieve "OR" processing logic for 2 requirement one must group them (put identical group ID).
    """

    EVENT_TYPES = Choices(*settings.BADGES_CONFIG['events'])

    template = models.ForeignKey(
        BadgeTemplate,
        on_delete=models.CASCADE,
        help_text=_("Badge template this requirement serves for."),
    )
    event_type = models.CharField(
        max_length=255,
        choices=EVENT_TYPES,
        help_text=_(
            'Public signal type. Use namespaced types, e.g: "org.openedx.learning.student.registration.completed.v1"'
        ),
    )
    description = models.TextField(
        null=True, blank=True, help_text=_("Provide more details if needed.")
    )

    def __str__(self):
        return f"BadgeRequirement:{self.id}:{self.template.uuid}"
    
    def save(self, *args, **kwargs):
        # Check if the related BadgeTemplate is active
        if not self.template.is_active:
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Cannot update BadgeRequirement for active BadgeTemplate")
    
    def is_fullfiled(self, username: str) -> bool:
        return self.fulfillment_set.filter(progress__username=username, progress__template=self.template).exists()


class DataRule(models.Model):
    """
    Specifies expected data attribute value for event payload.

    NOTE: all data rules for a single requirement follow "AND" processing logic.
    """

    OPERATORS = Choices(
        ("eq", "="),
        ("ne", "!="),
        # ('lt', '<'),
        # ('gt', '>'),
    )

    requirement = models.ForeignKey(
        BadgeRequirement,
        on_delete=models.CASCADE,
        help_text=_("Parent requirement for this data rule."),
    )
    data_path = models.CharField(
        max_length=255,
        help_text=_(
            'Public signal\'s data payload nested property path, e.g: "user.pii.username".'
        ),
        verbose_name=_("key path"),
    )
    operator = models.CharField(
        max_length=32,
        choices=OPERATORS,
        default=OPERATORS.eq,
        help_text=_(
            "Expected value comparison operator. https://docs.python.org/3/library/operator.html"
        ),
    )
    value = models.CharField(
        max_length=255,
        help_text=_('Expected value for the nested property, e.g: "cucumber1997".'),
        verbose_name=_("expected value"),
    )

    class Meta:
        unique_together = ("requirement", "data_path", "operator", "value")

    def __str__(self):
        return f"{self.requirement.template.uuid}:{self.data_path}:{self.operator}:{self.value}"
    
    def save(self, *args, **kwargs):
        if not is_datapath_valid(self.data_path, self.requirement.event_type):
            raise ValidationError("Invalid data path for event type")

        # Check if the related BadgeTemplate is active
        if not self.requirement.template.is_active:
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Cannot update DataRule for active BadgeTemplate")


class BadgeProgress(models.Model):
    """
    Tracks a single badge template progress for user.

    - allows multiple requirements status tracking;
    """

    credential = models.OneToOneField(
        UserCredential,
        models.SET_NULL,
        blank=True,
        null=True,
    )
    username = models.CharField(max_length=255)  # index
    template = models.ForeignKey(
        BadgeTemplate,
        models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = _("badge progress records")

    def __str__(self):
        return f"BadgeProgress:{self.username}"
    
    @property
    def ratio(self) -> float:
        """
        Calculate badge template progress ratio.
        """
        requirements_count = BadgeRequirement.objects.filter(template=self.template).count()
        if requirements_count == 0:
            raise ValueError("No requirements found for badge template")

        fulfilled_requirements_count = Fulfillment.objects.filter(progress=self, requirement__template=self.template).count()
        return fulfilled_requirements_count / requirements_count


class Fulfillment(models.Model):
    """
    Tracks completed badge template requirement for user.
    """

    progress = models.ForeignKey(BadgeProgress, on_delete=models.CASCADE)
    requirement = models.ForeignKey(
        BadgeRequirement,
        models.SET_NULL,
        blank=True,
        null=True,
    )


class CredlyBadge(UserCredential):
    """
    Earned Credly badge (Badge template credential) for user.

    - tracks distributed (external Credly service) state for Credly badge.
    """

    STATES = Choices(
        "created", "no_response", "error", "pending", "accepted", "rejected", "revoked"
    )

    state = StatusField(
        choices_name="STATES",
        help_text=_("Credly badge issuing state"),
        default=STATES.created,
    )
