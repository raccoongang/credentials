"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""

import logging
import uuid

from django.dispatch import receiver
from openedx_events.learning.data import BadgeData, BadgeTemplateData, CoursePassingStatusData, CcxCoursePassingStatusData
from openedx_events.learning.signals import BADGE_AWARDED, BADGE_REVOKED
from openedx_events.tooling import OpenEdxPublicSignal, load_all_signals

from credentials.apps.core.api import get_user_by_username

from ..services.badge_templates import get_badge_template_by_id
from ..services.user_credentials import create_user_credential
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
        signal.connect(processor)


def processor(sender, signal, **kwargs):
    """
    Event bus incoming public signals generic handler.

    NOTE (performance): all consumed messages from event bus trigger this.
    """
    logger.debug(f"Received signal {signal}")

    # incoming signals (e.g. Messages) processing pipeline:
    # - identify user in the Message;
    #   - check if such user exist (update or create);
    # - collect all Requirements for Message event type;
    #   - no Requirements - nothing to process - STOP;
    # - for each found Requirement:
    #   - see its `effect` (award | revoke)

    #   AWARD FLOW:
    #   - check if the related badge template already completed
    #       - if BadgeProgress exists and BadgeProgress.complete == true >> badge already earned - STOP;
    #   - check if it is not fulfilled yet
    #       - if fulfilled (related Fulfillment exists) - STOP;
    #   - apply payload rules (data-rules);
    #   - if applied - fulfill the Requirement:
    #       - create related Fulfillment
    #       - update of create BadgeProgress
    #   - BadgeProgress completeness check - check if it was enough for badge earning
    #       - if BadgeProgress.complete == true
    #           - emit BADGE_PROGRESS_COMPLETE >> handle_badge_completion
    #
    #   REVOKE FLOW:
    #   - TBD
    #   - ...
    #   - BADGE_PROGRESS_INCOMPLETE emitted >> handle_badge_regression (possibly, we need a flag here)

    # hardcode-processing:
    course_passing_status = kwargs.get("course_passing_status", None)

    if course_passing_status.status == CoursePassingStatusData.PASSING:
        BADGE_PROGRESS_COMPLETE.send(sender=sender, username=kwargs.get("course_passing_status").user.pii.username, badge_template_id=1)  # temporarily faked badge_template_id

    if course_passing_status.status == CoursePassingStatusData.FAILING:
        BADGE_PROGRESS_INCOMPLETE.send(sender=sender, username=kwargs.get("course_passing_status").user.pii.username, badge_template_id=1)  # temporarily faked badge_template_id


@receiver(BADGE_PROGRESS_COMPLETE)
def handle_badge_completion(sender, username, badge_template_id, **kwargs):  # pylint: disable=unused-argument
    """
    On user's Badge completion.

    - username
    - badge template ID
    """

    badge_template = get_badge_template_by_id(badge_template_id)
    user = get_user_by_username(username)

    if badge_template.origin == "openedx":
        # instead we need to make badge template type responsible for user credential creation:
        # badge_template.award(username) --> creates corresponding type of user-credential
        create_user_credential(username, badge_template)

    # UserCredential.as_badge_data() - user-credential is responsible for its conversion into payload:
    badge_data = BadgeData(
        uuid=uuid.uuid1(),
        user=user,
        template=BadgeTemplateData(
            uuid=str(badge_template.uuid),
            type=badge_template.origin,
            name=badge_template.name,
            description=badge_template.description,
            image_url=badge_template.icon.url,
        ),
    )

    BADGE_AWARDED.send_event(badge=badge_data)


@receiver(BADGE_PROGRESS_INCOMPLETE)
def handle_badge_regression(sender, username, badge_template_id, **kwargs):  # pylint: disable=unused-argument
    """
    On user's Badge regression (incompletion).
    """

    badge_template = get_badge_template_by_id(badge_template_id)
    user = get_user_by_username(username)

    # UserCredential.as_badge_data():
    badge_data = BadgeData(
        uuid=uuid.uuid1(),
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
