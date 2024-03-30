"""
Revocation pipeline - badge regression.
"""
import uuid

from openedx_events.learning.data import BadgeData, BadgeTemplateData, UserData, UserPersonalData
from openedx_events.learning.signals import BADGE_REVOKED

from ..models import CredlyBadgeTemplate


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
        uuid=uuid.uuid4(),
        user=UserData(
            pii=UserPersonalData(
                username='event_user-username',
                email='event_user-email',
                name='event_user-name',
            ),
            id='event_user-id',
            is_active=True,
        ),
        template=BadgeTemplateData(
            uuid=str(badge_template.uuid),
            origin=badge_template.origin,
            name=badge_template.name,
            description=badge_template.description,
            image_url=badge_template.icon,
        ),
    )

    BADGE_REVOKED.send_event(badge=badge_data)
