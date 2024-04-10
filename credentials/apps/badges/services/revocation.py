"""
Revocation pipeline - badge regression.
"""

import uuid
from typing import List

from openedx_events.learning.data import (
    BadgeData,
    BadgeTemplateData,
    UserData,
    UserPersonalData,
)
from openedx_events.learning.data import CoursePassingStatusData
from openedx_events.learning.signals import BADGE_REVOKED

from credentials.apps.badges.signals.signals import BADGE_PROGRESS_INCOMPLETE
from credentials.apps.badges.utils import keypath
from credentials.apps.badges.models import BadgePenalty, CredlyBadgeTemplate


def discover_penalties(event_type: str) -> List[BadgePenalty]:
    return BadgePenalty.objects.filter(event_type=event_type)


def process_penalties(event_type, username, payload_dict):
    """
    REVOKE FLOW:
    - check if the related badge template already completed
        - if BadgeProgress exists and BadgeProgress.complete == true >> badge already earned - STOP;
    - check if it is not fulfilled yet
        - if fulfilled (related Fulfillment exists) - STOP;
    - apply payload rules (data-rules);
    - if applied - fulfill the Requirement:
        - create related Fulfillment
        - update of create BadgeProgress
    - BadgeProgress completeness check - check if it was enough for badge earning
        - if BadgeProgress.complete == false
            - emit BADGE_PROGRESS_INCOMPLETE >> handle_badge_incompletion
    """

    # TEMP: remove this stub after processing is implemented

    if keypath(payload_dict, "course_passing_status.status") == CoursePassingStatusData.FAILING:
        BADGE_PROGRESS_INCOMPLETE.send(
            sender=None,
            username=username,
            badge_template_id=CredlyBadgeTemplate.objects.first().id,
        )

    # :TEMP

    penalties = discover_penalties(event_type=event_type)
    for penalty in penalties:
        if not penalty.is_active:
            continue
        if penalty.apply_rules(payload_dict):
            penalty.reset_requirements(username)


def notify_badge_revoked(user_credential):  # pylint: disable=unused-argument
    """
    Emit public event about badge template regression.

    - username
    - badge template ID
    """

    # TODO: make user-credential responsible for its conversion into signal payload:
    # e.g.: badge_data = CredlyBadge.as_badge_data()

    badge_data = BadgeData(
        uuid=str(uuid.uuid4()),
        user=UserData(
            pii=UserPersonalData(
                username="event_user-username",
                email="event_user-email",
                name="event_user-name",
            ),
            id=1,
            is_active=True,
        ),
        template=BadgeTemplateData(
            uuid=str(uuid.uuid4()),
            origin="faked.origin",
            name="faked.name",
            description="feaked.description",
            image_url="faked.badge_template.icon",
        ),
    )

    BADGE_REVOKED.send_event(badge=badge_data)
