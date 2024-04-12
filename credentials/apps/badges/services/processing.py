"""
Main processing logic.
"""

import logging

from credentials.apps.badges.exceptions import (
    BadgesProcessingError,
    StopEventProcessing,
)
from credentials.apps.core.api import get_or_create_user_from_event_data

from ..services.awarding import process_requirements
from ..services.revocation import process_penalties
from ..utils import extract_payload, get_user_data


logger = logging.getLogger(__name__)


def process_event(sender, **kwargs):
    """
    Badge templates configuration interpreter.

    Responsibilities:
        - event's User identification (whose action);
        - requirements processing;
        - penalties processing;
    """

    event_type = sender.event_type

    try:
        # user identification
        username = identify_user(event_type=event_type, event_payload=extract_payload(kwargs, as_dict=True))

        # requirements processing
        process_requirements(event_type, username, extract_payload(kwargs, as_dict=True))

        # penalties processing
        process_penalties(event_type, username, extract_payload(kwargs, as_dict=True))

    except StopEventProcessing:
        # controlled processing dropping
        return

    except BadgesProcessingError as error:
        logger.error(f"Badges processing error: {error}")
        return


def identify_user(*, event_type, event_payload):
    """
    Identifies event user based on provided keyword arguments and returns the username.

    This function extracts user data from the given event's keyword arguments, attempts to identify existing user
    or creates a new user based on this data, and then returns the username.

    Args:
        **kwargs: public event keyword arguments containing user identification data.

    Returns:
        str: The username of the identified (and created if needed) user.

    Raises:
        BadgesProcessingError: if user data was not found.
    """

    user_data = get_user_data(event_payload)

    # FIXME: didn't find!
    user_data = event_payload["course_passing_status"].user

    if not user_data:
        message = f"User data cannot be found (got: {user_data}): {event_payload}. Does event {event_type} include user data at all?"
        raise BadgesProcessingError(message)

    user, __ = get_or_create_user_from_event_data(user_data)
    return user.username
