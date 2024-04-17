"""
Badge regression processing.
"""

import logging
from typing import List

from credentials.apps.badges.models import BadgePenalty


logger = logging.getLogger(__name__)


def discover_penalties(event_type: str) -> List[BadgePenalty]:
    """
    Picks all relevant penalties based on the event type.
    """

    # TODO: get only active templates
    return BadgePenalty.objects.filter(event_type=event_type)


def process_penalties(event_type, username, payload_dict):
    """
    Finds all relevant penalties, tests them one by one, marks related requirement as not completed if needed.
    """

    penalties = discover_penalties(event_type=event_type)

    logger.debug("BADGES: found %s penalties to process.", len(penalties))

    for penalty in penalties:

        # TODO: remove the check if only active templates were collected
        if not penalty.is_active:
            continue

        # process: payload rules
        if penalty.apply_rules(payload_dict):
            penalty.reset_requirements(username)
