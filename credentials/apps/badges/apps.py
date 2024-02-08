from django.apps import AppConfig
from django.conf import settings

from credentials.apps.plugins.constants import PROJECT_TYPE, PluginSettings, PluginURLs, SettingsType

from .toggles import check_badges_enabled, is_badges_enabled


class BadgesAppConfig(AppConfig):
    """
    Extended application config with additional Badges-specific logic.
    """

    @property
    def verbose_name(self):
        return f"Badges: {self.plugin_label}"


class BadgesConfig(BadgesAppConfig):
    """
    Core badges application configuration.
    """
    default = True
    name = "credentials.apps.badges"
    verbose_name = "Badges"

    @check_badges_enabled
    def ready(self):
        """
        Activate installed badges plugins if they are enabled.

        Performs initial registrations for checks, signals, etc.
        """
        from .checks import badges_checks  # pylint: disable=unused-import,import-outside-toplevel
        from .signals import collecting  # pylint: disable=unused-import,import-outside-toplevel

        super().ready()
