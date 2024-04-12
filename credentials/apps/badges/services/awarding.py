"""
Awarding pipeline - badge progression.
"""

from typing import List

from openedx_events.learning.signals import BADGE_AWARDED

from credentials.apps.badges.models import BadgeRequirement
from credentials.apps.badges.signals import BADGE_PROGRESS_COMPLETE


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

    requirements = discover_requirements(event_type=event_type)
    completed_templates = set()

    for requirement in requirements:
        if requirement.template.user_completion(username):
            completed_templates.add(requirement.template_id)
        
        if requirement.template_id not in completed_templates:
            if not requirement.is_active or requirement.is_fulfilled(username):
                continue

        if requirement.apply_rules(payload_dict):
            requirement.fulfill(username)


def notify_badge_awarded(user_credential):  # pylint: disable=unused-argument
    """
    Emit public event about badge template completion.

    - username
    - badge template ID
    """

    badge_data = user_credential.as_badge_data()
    BADGE_AWARDED.send_event(badge=badge_data)
