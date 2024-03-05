from django.conf import settings


def get_badging_event_types():
    """
    Figures out which events are available for badges.
    """
    return settings.BADGES_CONFIG.get('events', [])