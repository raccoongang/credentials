"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""


def process(sender, **kwargs):
    """
    Find and process relevant requirements for a given event type.

    - find all relevant Requirement records;
    - update corresponding Fulfillments for event user;
    """
    pass


def collect(sender, **kwargs):
    """ """
    pass
