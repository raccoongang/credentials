"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""
import logging

from django.dispatch import receiver

from openedx_events.learning.data import BadgeData, BadgeTemplateData
from openedx_events.learning.signals import BADGE_REVOKED
from openedx_events.tooling import OpenEdxPublicSignal, load_all_signals

from apps.core.api import get_user_by_username

from .signals import BADGE_PROGRESS_INCOMPLETE
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


@receiver(BADGE_PROGRESS_INCOMPLETE)
def listen_for_incompleted_badge(sender, username, badge_template_id, **kwargs):  # pylint: disable=unused-argument
    badge_template = get_badge_template_by_id(badge_template_id)
    user = get_user_by_username(username)

    badge = revoke_badge() # function needs to be implemented

    badge_data = BadgeData(
        uuid=badge.uuid,
        user=user,
        template=BadgeTemplateData(
            uuid=str(badge_template.uuid),
            type=badge_template.origin,
            name=badge_template.name,
            description=badge_template.description,
            image_url=badge_template.icon.url,
        ),
    )
    BADGE_REVOKED.send_event(badge=badge_data)
