import attr
import inspect

from attrs import asdict
from django.conf import settings

from openedx_events.learning.data import UserData


def get_badging_event_types():
    """
    Figures out which events are available for badges.
    """
    return settings.BADGES_CONFIG.get("events", [])


def keypath(payload, keys_path):
    """
    Retrieve the value from a nested dictionary using a dot-separated key path.

    Traverses a nested dictionary `payload` to find the value specified by the dot-separated
    key path `keys_path`. Each key in `keys_path` represents a level in the nested dictionary.

    Parameters:
    - payload (dict): The nested dictionary to search.
    - keys_path (str): The dot-separated path of keys to traverse in the dictionary.

    Returns:
        - The value found at the specified key path in the dictionary, or None if any key in the path
        does not exist or the traversal leads to a non-dictionary object before reaching the final key.

    Example:
    >>> payload = {'a': {'b': {'c': 1}}}
    >>> keypath(payload, 'a.b.c')
    1
    >>> keypath(payload, 'a.b.d')
    None
    """
    keys = keys_path.split(".")
    current = payload

    def traverse(current, keys):
        if not keys:
            return current
        key = keys[0]
        if attr.has(current):
            current = asdict(current)
        if isinstance(current, dict) and key in current:
            return traverse(current[key], keys[1:])
        else:
            return None

    return traverse(current, keys)


def get_user_data(data) -> UserData:
    """
    Extracts UserData object from any dataclass that contains UserData as a field.
    Arguments:
        data: Input dataclass object that contains UserData.
    Returns:
        UserData: UserData object contained within the input dataclass.
    """
    # Check if the data is an instance of UserData directly
    if isinstance(data, UserData):
        return data
    # Inspect attributes of the dataclass
    for attr_name, attr_value in inspect.getmembers(data):
        # Check if the attribute is an instance of UserData
        if isinstance(attr_value, UserData):
            return attr_value
        # If the attribute is an instance of another dataclass, recursively search for UserData
        elif attr_value is not None and attr_name != "pii" and hasattr(attr_value, "__attrs_attrs__"):
            user_data = get_user_data(attr_value)
            if user_data:
                return user_data
    # UserData not found in the dataclass or its attributes
    return None
