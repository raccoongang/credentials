"""
These signal handlers are auto-subscribed to all expected badging signals (event types).

See:
"""
import logging

logger = logging.getLogger(__name__)


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


def general_signal_handler(sender, signal, **kwargs):
    logger.info(f'Received signal {signal}')
