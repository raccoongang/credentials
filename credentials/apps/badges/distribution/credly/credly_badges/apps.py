from credentials.apps.badges.apps import BadgesAppConfig
from credentials.apps.badges.toggles import check_badges_enabled
from credentials.apps.plugins.constants import (
    PROJECT_TYPE,
    PluginSettings,
    PluginURLs,
    SettingsType,
)


class CredlyBadgesConfig(BadgesAppConfig):
    """
    Credly distribution backend.

    This app is the Credential service plugin.
    It is built on the top of the `credentials.apps.badges`.
    It allows configuration and issuance specific to the Credly (by Pearson) badges from Open edX.

    In addition in a context of Credly Organization:
    - organization badge templates are used to setup Open edX badge templates;
    - earned badges are distributed to the Credly service;
    """

    name = "credly_badges"
    plugin_label = "Credly (by Pearson)"
    default = True

    plugin_app = {
        PluginURLs.CONFIG: {
            PROJECT_TYPE: {
                PluginURLs.NAMESPACE: "credly_badges",
                PluginURLs.REGEX: "credly-badges/",
                PluginURLs.RELATIVE_PATH: "urls",
            }
        },
        PluginSettings.CONFIG: {
            PROJECT_TYPE: {
                SettingsType.BASE: {PluginSettings.RELATIVE_PATH: "settings.base"},
                SettingsType.PRODUCTION: {PluginSettings.RELATIVE_PATH: "settings.production"},
                SettingsType.TEST: {PluginSettings.RELATIVE_PATH: "settings.test"},
            },
        },
        # register signal handlers?
    }

    @check_badges_enabled
    def ready(self):
        """
        Performs initial registrations for checks, signals, etc.
        """
        super().ready()
