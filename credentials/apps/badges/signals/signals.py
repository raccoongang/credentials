"""
Badges internal signals:
- BADGE_REQUIREMENT_FULFILLED - a single requirement for badge template has finished;
- BADGE_REQUIREMENT_REGRESSED - a single requirement for badge template with revoke effect has happened;
- BADGE_PROGRESS_COMPLETE - all badge template requirements are finished;
- BADGE_PROGRESS_INCOMPLETE - a reason for earned badge revocation;
"""

from django.dispatch import Signal


BADGE_PROGRESS_COMPLETE = Signal()
BADGE_PROGRESS_INCOMPLETE = Signal()
