from django.dispatch import Signal

"""
define internal signals:
- BADGE_REQUIREMENT_FULFILLED - a single specific requirement has finished;
- BADGE_REQUIREMENTS_COMPLETE - all badge template requirements are finished;
- BADGE_REQUIREMENTS_NOT_COMPLETE - a reason for earned badge revocation;
"""

from django.dispatch import Signal

BADGE_PROGRESS_COMPLETE = Signal()
BADGE_PROGRESS_INCOMPLETE = Signal()
