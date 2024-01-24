"""
Credly Badges routing configuration.
"""

from credentials.apps.badges.toggles import is_badges_enabled

urlpatterns = []

if is_badges_enabled():
    urlpatterns = [
        # Define urls here
    ]