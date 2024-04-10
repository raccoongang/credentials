"""
Awarding pipeline - badge progression.
"""

import uuid
from typing import List

from openedx_events.learning.signals import BADGE_AWARDED

from credentials.apps.badges.models import BadgeRequirement, CredlyBadgeTemplate, UserCredential
from credentials.apps.badges.signals import BADGE_PROGRESS_COMPLETE
from credentials.apps.badges.utils import keypath


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

    for requirement in requirements:
        if not requirement.is_active:
            continue
        if requirement.apply_rules(payload_dict):
            requirement.fulfill(username)


def notify_badge_awarded(user_credential):  # pylint: disable=unused-argument
    """
    Emit public event about badge template completion.

    - username
    - badge template ID
    """

    # user = get_user_by_username(username)

    badge_data = UserCredential.objects.get(username=username, credential__uuid=badge_template_uuid).as_badge_data()
    BADGE_AWARDED.send_event(badge=badge_data)
