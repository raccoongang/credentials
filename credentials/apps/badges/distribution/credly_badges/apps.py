from django.apps import AppConfig
from credentials.apps.plugins.constants import (
    PluginURLs,
    PluginSettings,
    SettingsType,
    PROJECT_TYPE,
)


class CredlyBadgesConfig(AppConfig):
    name = "credentials.apps.badges.distribution.credly_badges"
    verbose_name = "Credly badges"

    plugin_app = {
        PluginURLs.CONFIG: {
            PROJECT_TYPE: {
                PluginURLs.NAMESPACE: 'credly_badges',
                PluginURLs.REGEX: 'credly-badges/',
                PluginURLs.RELATIVE_PATH: 'urls',
            }
        },
        PluginSettings.CONFIG: {
            PROJECT_TYPE: {
                SettingsType.BASE: {PluginSettings.RELATIVE_PATH: 'settings.base'},
                SettingsType.PRODUCTION: {PluginSettings.RELATIVE_PATH: 'settings.production'},
                SettingsType.TEST: {PluginSettings.RELATIVE_PATH: 'settings.test'},
            },
        }
    }
