"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""
import logging
from openedx_events.learning.signals import BADGE_AWARDED, BADGE_REVOKED
from openedx_events.learning.data import BadgeData, BadgeTemplateData
from credentials.apps.badges.models import BadgeTemplate

logger = logging.getLogger(__name__)


def process(sender, **kwargs):
    """
    Find and process relevant requirements for a given event type.

    - find all relevant Requirement records;
    - update corresponding Fulfillments for event user;
    """

    # FIXME: this is a temporary solution for testing purposes
    badge_template = BadgeTemplate.objects.last()
    badge_data = BadgeData(
        uuid='badge-uuid',
        user=kwargs.get('user_course_data').user,
        template=BadgeTemplateData(
            uuid=str(badge_template.uuid),
            type=badge_template.origin,
            name=badge_template.name,
            description=badge_template.description,
            image_url=badge_template.icon.url,
        ),
    )

    if sender == 'org.openedx.learning.course.grade.now.passed.v1':
        BADGE_AWARDED.send_event(badge=badge_data)
    elif sender == 'org.openedx.learning.course.grade.now.failed.v1':
        BADGE_REVOKED.send_event(badge=badge_data)


def collect(sender, **kwargs):
    """ """
    pass


def general_signal_handler(sender, signal, **kwargs):
    logger.info(f'Received signal {signal}')
    process(signal.event_type, **kwargs)
