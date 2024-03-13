"""
Credly Badges routing configuration.
"""

from django.urls import path

from credentials.apps.badges.toggles import is_badges_enabled

from .rest_api import CredlyWebhook


urlpatterns = []

if is_badges_enabled():
    urlpatterns = [
        path("api/webhook/", CredlyWebhook.as_view(), name="credly-webhook"),
    ]
