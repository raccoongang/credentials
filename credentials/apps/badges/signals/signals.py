"""
define internal signals:
- BADGE_REQUIREMENT_FULFILLED - a single specific requirement has finished;
- BADGE_REQUIREMENTS_COMPLETE - all badge template requirements are finished;
- BADGE_REQUIREMENTS_NOT_COMPLETE - a reason for earned badge revocation;
"""

from django.dispatch import Signal

# Signal that indicates that user finisher all badge template requirements.
# providing_args=[
#         'username',  # String usernam of User
#         'badge_template_id',  # Integer ID of finished badge template
#     ]
BADGE_PROGRESS_COMPLETE = Signal()

