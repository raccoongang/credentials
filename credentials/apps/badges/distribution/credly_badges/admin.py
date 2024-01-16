"""
Admin section configuration for credly badges.
"""

from .toggles import is_credly_badges_enabled

if is_credly_badges_enabled():
    # TODO: Define registering admin classes here `admin.site.register(...)`
    pass
