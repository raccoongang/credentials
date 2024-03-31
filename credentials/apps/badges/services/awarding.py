"""
Awarding pipeline - badge progression.
"""
import uuid

from openedx_events.learning.data import BadgeData, BadgeTemplateData, UserData, UserPersonalData
from openedx_events.learning.signals import BADGE_AWARDED

from ..models import CredlyBadgeTemplate


def notify_badge_awarded(username, badge_template_uuid):  # pylint: disable=unused-argument
    """
    Emit public event about badge template completion.

    - username
    - badge template ID
    """

    badge_template = CredlyBadgeTemplate.by_uuid(badge_template_uuid)
    # user = get_user_by_username(username)

    # UserCredential.as_badge_data() - user-credential is responsible for its conversion into payload:
    badge_data = BadgeData(
        uuid=str(uuid.uuid4()),
        user=UserData(
            pii=UserPersonalData(
                username='event_user-username',
                email='event_user-email',
                name='event_user-name',
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

    BADGE_AWARDED.send_event(badge=badge_data)