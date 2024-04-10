"""
Awarding pipeline - badge progression.
"""

from typing import List

from openedx_events.learning.signals import BADGE_AWARDED

from ..models import BadgeRequirement, UserCredential


def notify_badge_awarded(username, badge_template_uuid):  # pylint: disable=unused-argument
    """
    Emit public event about badge template completion.

    - username
    - badge template ID
    """

    # user = get_user_by_username(username)

    badge_data = UserCredential.objects.get(username=username, credential__uuid=badge_template_uuid).as_badge_data()
    BADGE_AWARDED.send_event(badge=badge_data)


def discover_requirements(event_type: str) -> List[BadgeRequirement]:
    return BadgeRequirement.objects.filter(event_type=event_type)
