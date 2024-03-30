"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""

import logging

from django.dispatch import receiver
from openedx_events.tooling import OpenEdxPublicSignal, load_all_signals

from ..services.awarding import notify_badge_awarded
from ..services.processing import process_event
from ..services.revocation import notify_badge_revoked
from ..utils import get_badging_event_types
from .signals import BADGE_PROGRESS_COMPLETE, BADGE_PROGRESS_INCOMPLETE


logger = logging.getLogger(__name__)


def listen_to_badging_events():
    """
    Connects event handler to pre-configured public signals subset.
    """

    load_all_signals()

    for event_type in get_badging_event_types():
        signal = OpenEdxPublicSignal.get_signal_by_type(event_type)
        signal.connect(handle_badging_event, dispatch_uid=event_type)


def handle_badging_event(sender, signal, **kwargs):
    """
    Event bus incoming public signals generic handler.

    NOTE (performance): all consumed messages from event bus trigger this.
    """
    logger.debug(f"Received signal {signal}")

    process_event(signal, **kwargs)


@receiver(BADGE_PROGRESS_COMPLETE)
def handle_badge_completion(sender, username, badge_template_uuid, **kwargs):  # pylint: disable=unused-argument
    """
    On user's Badge completion.

    - username
    - badge template ID
    """

    # TODO: issue UserCredential
    # TODO: ussue Credly badge
    notify_badge_awarded(username, badge_template_uuid)


@receiver(BADGE_PROGRESS_INCOMPLETE)
def handle_badge_regression(sender, username, badge_template_uuid, **kwargs):  # pylint: disable=unused-argument
    """
    On user's Badge regression (incompletion).

    - username
    - badge template ID
    """

    # TODO: change UserCredential's status to revoked
    # TODO: revoke Credly badge
    notify_badge_revoked(username, badge_template_uuid)
