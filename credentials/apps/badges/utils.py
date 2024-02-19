from django.conf import settings
from openedx_events.tooling import OpenEdxPublicSignal, load_all_signals

from .signals.handlers import general_signal_handler


def connect_generic_signal_to_events():
    """
    Connect the generic signal handler to all listened events.
    """

    load_all_signals()

    for event_type in settings.BADGES_CONFIG.get('events', []):
        signal = OpenEdxPublicSignal.get_signal_by_type(event_type)
        signal.connect(general_signal_handler)
