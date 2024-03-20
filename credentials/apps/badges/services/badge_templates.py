from django.core.exceptions import ObjectDoesNotExist

from ..models import BadgeTemplate

def get_badge_template_by_id(badge_template_id):
    try:
        return BadgeTemplate.objects.get(id=badge_template_id)
    except ObjectDoesNotExist:
        return None
