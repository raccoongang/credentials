"""
Badges internal signals.
"""

from django.dispatch import Signal


# a single requirements for a badge template was finished
BADGE_REQUIREMENT_FULFILLED = Signal()

# a single penalty worked on a badge template
BADGE_REQUIREMENT_REGRESSED = Signal()

# all badge template requirements are finished
BADGE_PROGRESS_COMPLETE = Signal()

# badge template penalty reset some of fulfilled requirements, so badge template became incomplete
BADGE_PROGRESS_INCOMPLETE = Signal()
