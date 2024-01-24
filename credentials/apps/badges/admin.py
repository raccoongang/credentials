"""
Admin section configuration.
"""
from django.contrib import admin

from .toggles import is_badges_enabled


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    pass