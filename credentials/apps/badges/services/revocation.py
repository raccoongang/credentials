"""
Revocation pipeline - badge regression.
"""

from typing import List

from openedx_events.learning.signals import BADGE_REVOKED

from ..models import BadgePenalty, UserCredential


def notify_badge_revoked(username, badge_template_uuid):  # pylint: disable=unused-argument
    """
    Emit public event about badge template regression.

    - username
    - badge template ID
    """

    # user = get_user_by_username(username)

    badge_data = UserCredential.objects.get(username=username, credential__uuid=badge_template_uuid).as_badge_data()
    BADGE_REVOKED.send_event(badge=badge_data)


def discover_penalties(event_type: str) -> List[BadgePenalty]:
    return BadgePenalty.objects.filter(event_type=event_type)
