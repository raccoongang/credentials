"""
Badges internal signals.
"""

from django.dispatch import Signal
from openedx_events.learning.signals import BADGE_AWARDED, BADGE_REVOKED


# a single requirements for a badge template was finished
BADGE_REQUIREMENT_FULFILLED = Signal()

# a single penalty worked on a badge template
BADGE_REQUIREMENT_REGRESSED = Signal()

# all badge template requirements are finished
BADGE_PROGRESS_COMPLETE = Signal()

# badge template penalty reset some of fulfilled requirements, so badge template became incomplete
BADGE_PROGRESS_INCOMPLETE = Signal()


def notify_requirement_fulfilled(*, sender, username, badge_template_id, **kwargs):
    """
    Notifies about user's progression on the badge template.
    """

    BADGE_REQUIREMENT_FULFILLED.send(
        sender=sender,
        username=username,
        badge_template_id=badge_template_id,
    )


def notify_requirement_regressed(*, sender, username, badge_template_id):
    """
    FIXME: implement/use
    """


def notify_progress_complete(sender, username, badge_template_id):
    """
    FIXME:
    """
    BADGE_PROGRESS_COMPLETE.send(
        sender=sender,
        username=username,
        badge_template_id=badge_template_id,
    )


def notify_progress_incomplete(sender, username, badge_template_id):
    """
    FIXME: implement/use
    """
    BADGE_PROGRESS_INCOMPLETE.send(
        sender=sender,
        username=username,
        badge_template_id=badge_template_id,
    )


def notify_badge_awarded(user_credential):  # pylint: disable=unused-argument
    """
    Emit public event about badge template completion.

    - username
    - badge template ID
    """

    BADGE_AWARDED.send_event(badge=user_credential.as_badge_data())


def notify_badge_revoked(user_credential):  # pylint: disable=unused-argument
    """
    Emit public event about badge template regression.

    - username
    - badge template ID
    """

    BADGE_REVOKED.send_event(badge=user_credential.as_badge_data())
