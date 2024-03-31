"""
URLs for badges.
"""

from django.urls import path

from credentials.apps.badges.toggles import is_badges_enabled

from .credly.webhooks import CredlyWebhook
from .toggles import is_badges_enabled


urlpatterns = []

if is_badges_enabled():
    urlpatterns = [
        path("api/webhook/", CredlyWebhook.as_view(), name="credly-webhook"),
    ]