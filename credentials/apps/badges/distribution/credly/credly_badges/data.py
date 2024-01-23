import attr
from datetime import datetime


@attr.s(auto_attribs=True, frozen=True)
class IssueBadgeData:
    """
    Represents the data required to issue a badge.

    Attributes:
        recipient_email (str): Email address of the badge recipient.
        issued_to_first_name (str): First name of the badge recipient.
        issued_to_last_name (str): Last name of the badge recipient.
        badge_template_id (str): ID of the badge template.
        issued_at (datetime): Timestamp when the badge was issued.
    """

    recipient_email: attr.ib(type=str)
    issued_to_first_name: attr.ib(type=str)
    issued_to_last_name: attr.ib(type=str)
    badge_template_id: attr.ib(type=str)
    issued_at: attr.ib(type=datetime)
