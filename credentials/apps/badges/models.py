"""
Badges DB models.
"""

import operator
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from model_utils.fields import StatusField
from openedx_events.learning.data import BadgeData, BadgeTemplateData, UserData, UserPersonalData

from credentials.apps.core.api import get_user_by_username
from credentials.apps.badges.signals import BADGE_REQUIREMENT_FULFILLED, BADGE_REQUIREMENT_REGRESSED
from credentials.apps.badges.utils import is_datapath_valid, keypath
from credentials.apps.credentials.models import AbstractCredential, UserCredential


class CredlyOrganization(TimeStampedModel):
    """
    Credly Organization configuration.
    """

    uuid = models.UUIDField(unique=True, help_text=_("Put your Credly Organization ID here."))
    api_key = models.CharField(max_length=255, help_text=_("Credly API shared secret for Credly Organization."))
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


class AbstractDataRule(models.Model):
    """
    Abstract DataRule configuration model.

    .. no_req_or_pen: This model has no requirement or penalty.
    """

    OPERATORS = Choices(
        ("eq", "="),
        ("ne", "!="),
        # ('lt', '<'),
        # ('gt', '>'),
    )

    data_path = models.CharField(
        max_length=255,
        help_text=_('Public signal\'s data payload nested property path, e.g: "user.pii.username".'),
        verbose_name=_("key path"),
    )
    operator = models.CharField(
        max_length=32,
        choices=OPERATORS,
        default=OPERATORS.eq,
        help_text=_("Expected value comparison operator. https://docs.python.org/3/library/operator.html"),
    )
    value = models.CharField(
        max_length=255,
        help_text=_('Expected value for the nested property, e.g: "cucumber1997".'),
        verbose_name=_("expected value"),
    )

    class Meta:
        abstract = True


class BadgeTemplate(AbstractCredential):
    """
    Describes badge credential type.
    """

    ORIGIN = "openedx"

    STATES = Choices("draft", "active", "archived")

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, help_text=_("Unique badge template ID."))
    name = models.CharField(max_length=255, help_text=_("Badge template name."))
    description = models.TextField(null=True, blank=True, help_text=_("Badge template description."))
    icon = models.ImageField(upload_to="badge_templates/icons", null=True, blank=True)
    origin = models.CharField(max_length=128, null=True, blank=True, help_text=_("Badge template type."))
    state = StatusField(
        choices_name="STATES",
        help_text=_("Credly badge template state (auto-managed)."),
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active and self.badgerequirement_set.count() == 0:
            raise ValidationError("Badge template must have at least 1 Requirement set.")
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
        progress = BadgeProgress.objects.filter(username=username, template=self).first()
        if progress is None:
            return 0.00
        return progress.ratio

    def user_completion(self, username: str) -> bool:
        """
        Check if user completed badge template.
        """
        return self.user_progress(username) == 1.00


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
        return (
            f"{credly_host_base_url}/mgmt/organizations/{self.organization.uuid}/badges/templates/{self.uuid}/details"
        )


class BadgeRequirement(models.Model):
    """
    Describes what must happen and how such event will affect badge progress.

    NOTE:   Badge template's requirements implement "AND" processing logic (e.g. all requirements must be fulfilled).
            To achieve "OR" processing logic for 2 requirement one must group them (put identical group ID).
    """

    EVENT_TYPES = Choices(*settings.BADGES_CONFIG["events"])

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
    description = models.TextField(null=True, blank=True, help_text=_("Provide more details if needed."))

    group = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Group ID for requirements grouping."),
    )

    def __str__(self):
        return f"BadgeRequirement:{self.id}:{self.template.uuid}"

    def save(self, *args, **kwargs):
        if self.is_active:
            raise ValidationError("Configuration updates are blocked on active badge templates")

        super().save(*args, **kwargs)

    def reset(self, username: str):
        fulfillments = Fulfillment.objects.filter(
            requirement=self,
            progress__username=username,
        )
        fulfillments.delete()
        BADGE_REQUIREMENT_REGRESSED.send(sender=None, username=username, fulfillments=fulfillments)

    def is_fulfilled(self, username: str) -> bool:
        return self.fulfillment_set.filter(progress__username=username, progress__template=self.template).exists()

    def fulfill(self, username: str):
        progress, _ = BadgeProgress.objects.get_or_create(template=self.template, username=username)
        fulfillment = Fulfillment.objects.create(progress=progress, requirement=self)
        BADGE_REQUIREMENT_FULFILLED.send(sender=None, username=username, fulfillment=fulfillment)

    def apply_rules(self, data: dict) -> bool:
        for rule in self.datarule_set.all():
            comparison_func = getattr(operator, rule.operator, None)
            if comparison_func:
                data_value = str(keypath(data, rule.data_path))
                result = comparison_func(data_value, rule.value)
                if not result:
                    return False
        return True

    @property
    def is_active(self):
        return self.template.is_active


class DataRule(AbstractDataRule):
    """
    Specifies expected data attribute value for event payload.
    NOTE: all data rules for a single requirement follow "AND" processing logic.
    """

    requirement = models.ForeignKey(
        BadgeRequirement,
        on_delete=models.CASCADE,
        help_text=_("Parent requirement for this data rule."),
    )

    class Meta:
        unique_together = ("requirement", "data_path", "operator", "value")

    def __str__(self):
        return f"{self.requirement.template.uuid}:{self.data_path}:{self.operator}:{self.value}"

    def save(self, *args, **kwargs):
        if not is_datapath_valid(self.data_path, self.requirement.event_type):
            raise ValidationError("Invalid data path for event type")

        if self.is_active:
            raise ValidationError("Configuration updates are blocked on active badge templates")

        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.requirement.template.is_active


class BadgePenalty(models.Model):
    """
    Describes badge regression rules for particular BadgeRequirement.
    """

    EVENT_TYPES = Choices(*settings.BADGES_CONFIG["events"])

    template = models.ForeignKey(
        BadgeTemplate,
        on_delete=models.CASCADE,
        help_text=_("Badge template this penalty serves for."),
    )
    event_type = models.CharField(
        max_length=255,
        choices=EVENT_TYPES,
        help_text=_(
            'Public signal type. Use namespaced types, e.g: "org.openedx.learning.student.registration.completed.v1"'
        ),
    )
    requirements = models.ManyToManyField(
        BadgeRequirement,
        help_text=_("Badge requirements for which this penalty is defined."),
    )
    description = models.TextField(null=True, blank=True, help_text=_("Provide more details if needed."))

    class Meta:
        verbose_name_plural = "Badge penalties"

    def save(self, *args, **kwargs):
        if self.is_active:
            raise ValidationError("Configuration updates are blocked on active badge templates")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"BadgePenalty:{self.id}:{self.template.uuid}"

    class Meta:
        verbose_name_plural = "Badge penalties"

    def apply_rules(self, data: dict) -> bool:
        return all(rule.apply(data) for rule in self.rules.all())

    def reset_requirements(self, username: str):
        for requirement in self.requirements.all():
            requirement.reset(username)

    @property
    def is_active(self):
        return self.template.is_active


class PenaltyDataRule(AbstractDataRule):
    """
    Specifies expected data attribute value for penalty rule.
    NOTE: all data rules for a single penalty follow "AND" processing logic.
    """

    penalty = models.ForeignKey(
        BadgePenalty,
        on_delete=models.CASCADE,
        help_text=_("Parent penalty for this data rule."),
        related_name="rules",
    )

    class Meta:
        unique_together = ("penalty", "data_path", "operator", "value")

    def save(self, *args, **kwargs):
        if not is_datapath_valid(self.data_path, self.penalty.event_type):
            raise ValidationError("Invalid data path for event type")

        # Check if the related BadgeTemplate is active
        if self.is_active:
            raise ValidationError("Configuration updates are blocked on active badge templates")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.penalty.template.uuid}:{self.data_path}:{self.operator}:{self.value}"

    def apply(self, data: dict) -> bool:
        comparison_func = getattr(operator, self.operator, None)
        if comparison_func:
            data_value = str(keypath(data, self.data_path))
            return comparison_func(data_value, self.value)
        return False

    class Meta:
        unique_together = ("penalty", "data_path", "operator", "value")
    @property
    def is_active(self):
        return self.penalty.template.is_active


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
            return 0.00

        fulfilled_requirements_count = Fulfillment.objects.filter(
            progress=self, requirement__template=self.template
        ).count()
        if fulfilled_requirements_count == 0:
            return 0.00
        return round(fulfilled_requirements_count / requirements_count, 2)

    def reset(self):
        Fulfillment.objects.filter(progress=self).delete()

    def completed(self):
        return self.ratio == 1.00


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

    STATES = Choices("created", "no_response", "error", "pending", "accepted", "rejected", "revoked")

    state = StatusField(
        choices_name="STATES",
        help_text=_("Credly badge issuing state"),
        default=STATES.created,
    )

    def as_badge_data(self) -> BadgeData:
        user = get_user_by_username(self.username)
        badge_template = self.credential

        badge_data = BadgeData(
            uuid=self.uuid,
            user=UserData(
                pii=UserPersonalData(
                    username=self.username,
                    email=user.email,
                    name=user.get_full_name(),
                ),
                id=user.lms_user_id,
                is_active=user.is_active,
            ),
            template=BadgeTemplateData(
                uuid=str(badge_template.uuid),
                origin=badge_template.origin,
                name=badge_template.name,
                description=badge_template.description,
                image_url=str(badge_template.icon),
            ),
        )
        return badge_data

    @property
    def is_issued(self):
        return self.uuid and (self.state in ["pending", "accepted", "rejected"])
