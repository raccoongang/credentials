"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""

import logging

from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from openedx_events.tooling import OpenEdxPublicSignal, load_all_signals

from credentials.apps.badges.issuers import CredlyBadgeTemplateIssuer
from credentials.apps.badges.models import BadgeTemplate
from credentials.apps.badges.processing.generic import process_event
from credentials.apps.badges.signals import BADGE_REQUIREMENT_FULFILLED, BADGE_REQUIREMENT_REGRESSED
from credentials.apps.badges.signals.signals import BADGE_PROGRESS_COMPLETE, BADGE_PROGRESS_INCOMPLETE
from credentials.apps.badges.utils import get_badging_event_types


logger = logging.getLogger(__name__)


def listen_to_badging_events():
    """
    Subscribes the main processing handler to badging events subset.
    """

    load_all_signals()

    for event_type in get_badging_event_types():
        signal = OpenEdxPublicSignal.get_signal_by_type(event_type)
        signal.connect(handle_badging_event, dispatch_uid=event_type)


def handle_badging_event(sender, signal, **kwargs):
    """
    Generic handler for incoming from the Event bus public signals.
    """

    logger.debug(f"BADGES: incoming signal - {signal}")

    process_event(signal, **kwargs)


@receiver(BADGE_REQUIREMENT_FULFILLED)
def handle_requirement_fulfilled(sender, username, fulfillment, **kwargs):  # pylint: disable=unused-argument
    """
    Fires once a single requirement was marked as "done".
    """
    if not fulfillment.progress.completed():
        BADGE_PROGRESS_COMPLETE.send(
            sender=None,
            username=username,
            badge_template_id=fulfillment.progress.template.id,
        )


@receiver(BADGE_REQUIREMENT_REGRESSED)
def handle_requirement_regressed(sender, username, fulfillments, **kwargs):  # pylint: disable=unused-argument
    """
    Fires once a single requirement for a badge template was marked as "done".
    """
    for fulfillment in fulfillments:
        BADGE_PROGRESS_INCOMPLETE.send(
            sender=None,
            username=username,
            badge_template_id=fulfillment.progress.template.id,
        )


@receiver(BADGE_PROGRESS_COMPLETE)
def handle_badge_completion(sender, username, badge_template_id, **kwargs):  # pylint: disable=unused-argument
    """
    Fires once ALL requirements for a badge template were marked as "done".

    - username
    - badge template ID
    """

    CredlyBadgeTemplateIssuer().award(badge_template_id, username)


@receiver(BADGE_PROGRESS_INCOMPLETE)
def handle_badge_regression(sender, username, badge_template_id, **kwargs):  # pylint: disable=unused-argument
    """
    On user's Badge regression (incompletion).

    - username
    - badge template ID
    """

    CredlyBadgeTemplateIssuer().revoke(badge_template_id, username)


@receiver(pre_delete, sender=BadgeTemplate)
def prevent_deletion_if_active(sender, instance, **kwargs):
    """
    Forbids already activated badge templates deletion.
    """
    if instance.is_active:
        raise ValidationError("Cannot delete active BadgeTemplate instance.")
