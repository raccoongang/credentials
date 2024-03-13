"""
URLs for badges.
"""

from .toggles import is_badges_enabled

urlpatterns = []

if is_badges_enabled():
    urlpatterns = [
        # Define urls here
    ]
