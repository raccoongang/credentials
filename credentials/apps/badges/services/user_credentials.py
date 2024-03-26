from django.contrib.contenttypes.models import ContentType

from ..models import BadgeTemplate, UserCredential


def create_user_credential(username, badge_template):
    if not isinstance(username, str):
        raise ValueError("`username` must be a string")
    
    if not isinstance(badge_template, BadgeTemplate):
        raise TypeError("`badge_template` must be an instance of BadgeTemplate")


    UserCredential.objects.create(
        credential_content_type=ContentType.objects.get_for_model(
            badge_template),
        credential_id=badge_template.id,
        username=username,
    )
