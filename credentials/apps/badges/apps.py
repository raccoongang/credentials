from django.apps import AppConfig
from django.conf import settings
from edx_django_utils.plugins import add_plugins, get_plugin_apps

from credentials.apps.plugins.constants import PluginSettings, PluginURLs

from .toggles import check_badges_enabled


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
        from . import signals  # pylint: disable=unused-import,import-outside-toplevel
        from .checks import badges_checks  # pylint: disable=unused-import,import-outside-toplevel

        super().ready()
