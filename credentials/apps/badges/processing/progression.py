"""
Awarding pipeline - badge progression.
"""

from typing import List

from openedx_events.learning.signals import BADGE_AWARDED

from credentials.apps.badges.models import BadgeRequirement


def discover_requirements(event_type: str) -> List[BadgeRequirement]:
    """
    Picks all relevant requirements based on the event type.
    """
    return BadgeRequirement.objects.filter(event_type=event_type)


def process_requirements(event_type, username, payload_dict):
    """
    Finds all relevant requirements, tests them one by one, marks as completed if needed.
    """

    requirements = discover_requirements(event_type=event_type)
    completed_templates = set()

    for requirement in requirements:

        # ignore: if the badge template wasn't activated yet
        if not requirement.is_active:
            continue

        # remember: the badge template is already "done"
        if requirement.template.is_completed(username):
            completed_templates.add(requirement.template_id)

        # drop early: if the badge template is already "done"
        if requirement.template_id in completed_templates:
            continue

        # drop early: if the requirement is already "done"
        if requirement.is_fulfilled(username):
            continue

        # process: payload rules
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
