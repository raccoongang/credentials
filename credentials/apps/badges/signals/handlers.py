"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""
import logging

from django.dispatch import receiver

from openedx_events.learning.signals import BADGE_AWARDED
from openedx_events.tooling import OpenEdxPublicSignal, load_all_signals

from .signals import BADGE_PROGRESS_COMPLETE
from ..services.badge_templates import get_badge_template_by_id
from ..utils import get_badging_event_types
from ..processing import process


logger = logging.getLogger(__name__)


def listen_to_badging_events():
    """
    Connects event handler to pre-configured public signals subset.
    """

    load_all_signals()

    for event_type in get_badging_event_types():
        signal = OpenEdxPublicSignal.get_signal_by_type(event_type)
        signal.connect(event_handler)


def event_handler(sender, signal, **kwargs):
    """
    Generic signal handler.
    """
    logger.debug(f"Received signal {signal}")

    # NOTE (performance): all consumed messages from event bus trigger this.
    process(signal, sender=sender, **kwargs)


@receiver(BADGE_PROGRESS_COMPLETE)
def listen_for_completed_badge(sender, username, badge_template_id, **kwargs):  # pylint: disable=unused-argument
    badge_template = get_badge_template_by_id(badge_template_id)
    ...

    BADGE_AWARDED.send_event(badge=badge_template)
