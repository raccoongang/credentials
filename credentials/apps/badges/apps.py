from django.apps import AppConfig

from .toggles import check_badges_enabled


class BadgesConfig(AppConfig):
    name = "credentials.apps.badges"
    verbose_name = "Badges"

    @check_badges_enabled
    def ready(self):
        """
        Performs initial registrations for checks, signals, etc.
        """
        from . import signals  # pylint: disable=unused-import,import-outside-toplevel
        from . checks import badges_checks  # pylint: disable=unused-import,import-outside-toplevel
