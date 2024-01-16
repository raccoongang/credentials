from django.apps import AppConfig

from .toggles import is_badges_enabled


class BadgesConfig(AppConfig):
    name = "credentials.apps.badges"
    verbose_name = "Badges"

    def ready(self):
        """
        Performs initial registrations for checks, signals, etc.
        """
        if is_badges_enabled():
            from . import signals  # pylint: disable=unused-import,import-outside-toplevel
            from . checks import badges_checks  # pylint: disable=unused-import,import-outside-toplevel
