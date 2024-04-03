from typing import List

from ..models import BadgeRequirement

def discover_requirements(event_type: str) -> List[BadgeRequirement]:
    return BadgeRequirement.objects.filter(event_type=event_type)