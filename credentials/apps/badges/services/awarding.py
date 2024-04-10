"""
Awarding pipeline - badge progression.
"""

import uuid
from typing import List

from openedx_events.learning.data import (
    BadgeData,
    BadgeTemplateData,
    CoursePassingStatusData,
    UserData,
    UserPersonalData,
)
from openedx_events.learning.signals import BADGE_AWARDED

from ..models import BadgeRequirement, CredlyBadgeTemplate
from ..signals import BADGE_PROGRESS_COMPLETE
from ..utils import keypath


def discover_requirements(event_type: str) -> List[BadgeRequirement]:
    return BadgeRequirement.objects.filter(event_type=event_type)


def process_requirements(event_type, username, payload_dict):
    """
    AWARD FLOW:
    - check if the related badge template already completed
        - if BadgeProgress exists and BadgeProgress.complete == true >> badge already earned - STOP;
    - check if it is not fulfilled yet
        - if fulfilled (related Fulfillment exists) - STOP;
    - apply payload rules (data-rules);
    - if applied - fulfill the Requirement:
        - create related Fulfillment
        - update of create BadgeProgress
    - BadgeProgress completeness check - check if it was enough for badge earning
        - if BadgeProgress.complete == true
            - emit BADGE_PROGRESS_COMPLETE >> handle_badge_completion
    """

    # TEMP: remove this stub after processing is implemented
    if keypath(payload_dict, "course_passing_status.status") == CoursePassingStatusData.PASSING:
        BADGE_PROGRESS_COMPLETE.send(
            sender=None,
            username=username,
            badge_template_id=CredlyBadgeTemplate.objects.first().id,
        )

    # :TEMP

    requirements = discover_requirements(event_type=event_type)

    # actual processing goes here:

    # for requirement in requirements:
    #     requirement.apply_rules(**kwargs)
    #     requirement.fulfill(username)


def notify_badge_awarded(user_credential):  # pylint: disable=unused-argument
    """
    Emit public event about badge template completion.

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

    BADGE_AWARDED.send_event(badge=badge_data)
