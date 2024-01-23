"""
URLs for badges.
"""

from .toggles import is_badges_enabled

urlpatterns = [] if not is_badges_enabled else [
    # Define urls here
]
