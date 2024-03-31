"""
Main processing logic.
"""

from openedx_events.learning.data import CoursePassingStatusData

from ..models import CredlyBadgeTemplate
from ..utils import keypath
from ..signals import BADGE_PROGRESS_COMPLETE, BADGE_PROGRESS_INCOMPLETE


def process_event(sender, **kwargs):
    """
    Badge templates configuration interpreter.

    Responsibilities:
        - event's User identification (whose action);
        - ...
    """
    # create/update signal User:
    # user_data = get_user_data(kwargs) - not yet implemented
    # event_user = get_or_create_user_from_event_data(user_data)

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

    # faked: related to the BadgeRequirement template (in real processing):
    badge_template_uuid = CredlyBadgeTemplate.objects.first().uuid

    if (
        keypath(kwargs, "course_passing_status.status")
        == CoursePassingStatusData.PASSING
    ):
        BADGE_PROGRESS_COMPLETE.send(
            sender=sender,
            username=keypath(kwargs, "course_passing_status.user.pii.username"),
            badge_template_uuid=badge_template_uuid,
        )

    if (
        keypath(kwargs, "course_passing_status.status")
        == CoursePassingStatusData.FAILING
    ):
        BADGE_PROGRESS_INCOMPLETE.send(
            sender=sender,
            username=keypath(kwargs, "course_passing_status.user.pii.username"),
            badge_template_uuid=badge_template_uuid,
        )
