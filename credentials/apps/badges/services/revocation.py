"""
Revocation pipeline - badge regression.
"""

import operator
import uuid

from typing import List

from openedx_events.learning.data import BadgeData, BadgeTemplateData, UserData, UserPersonalData
from openedx_events.learning.signals import BADGE_REVOKED

from ..models import BadgePenalty, BadgeProgress, CredlyBadgeTemplate, Fulfillment
from ..utils import keypath


def notify_badge_revoked(username, badge_template_uuid):  # pylint: disable=unused-argument
    """
    Emit public event about badge template regression.

    - username
    - badge template ID
    """
    badge_template = CredlyBadgeTemplate.by_uuid(badge_template_uuid)
    # user = get_user_by_username(username)

    # UserCredential.as_badge_data():
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
            uuid=str(badge_template.uuid),
            origin=badge_template.origin,
            name=badge_template.name,
            description=badge_template.description,
            image_url=str(badge_template.icon),
        ),
    )

    BADGE_REVOKED.send_event(badge=badge_data)


def discover_penalties(event_type: str) -> List[BadgePenalty]:
    return BadgePenalty.objects.filter(event_type=event_type)


def apply_penalties(penalties: List[BadgePenalty], username, kwargs: dict):
    for penalty in penalties:
        for datarule in penalty.penaltydatarule_set.all():
            if not getattr(operator, datarule.operator)(datarule.value, keypath(kwargs, datarule.data_path)):
                break
        else:
            [
                fulfillment.progress.reset()
                for fulfillment in Fulfillment.objects.filter(
                    requirement__in=penalty.requirements.all(), progress__username=username
                )
            ]
