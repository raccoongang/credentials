# FIXME: this moves to badges.issuers
from typing import Union

from django.contrib.contenttypes.models import ContentType

from openedx_events.learning.data import UserData

from ..models import BadgeTemplate, UserCredential


def create_user_credential(username, badge_template):
    """
    TODO: backport Issuers
    https://github.com/raccoongang/credentials/blob/208a3637cdaabd4777fa5ac91bff49a42972034a/credentials/apps/credentials/issuers.py
    """
    if not isinstance(username, str):
        raise ValueError("`username` must be a string")

    if not isinstance(badge_template, BadgeTemplate):
        raise TypeError("`badge_template` must be an instance of BadgeTemplate")

    UserCredential.objects.create(
        credential_content_type=ContentType.objects.get_for_model(badge_template),
        credential_id=badge_template.id,
        username=username,
    )
