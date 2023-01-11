"""  # lint-amnesty, pylint: disable=django-not-configured
Setup script for the Open edX credentials package.
"""

from setuptools import setup
from credentials.apps.plugins.constants import PROJECT_TYPE


setup(
    name="Open edX Credentials",
    version="0.1",
    install_requires=["setuptools"],
    requires=[],
    packages=["credentials"],
    package_data={},
    entry_points={
        PROJECT_TYPE: [
            "plugins = credentials.apps.plugins.apps:PluginsConfig",
        ],
    },
)
