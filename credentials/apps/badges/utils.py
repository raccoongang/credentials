import inspect

import attr
from attrs import asdict
from django.conf import settings
from openedx_events.learning.data import UserData, UserPersonalData
from openedx_events.tooling import OpenEdxPublicSignal


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


def is_datapath_valid(datapath: str, event_type: str) -> bool:
    path = datapath.split(".")
    event_types = get_badging_event_types()
    if event_type not in event_types:
        return False
    try:
        obj = OpenEdxPublicSignal.get_signal_by_type(event_type).init_data[path[0]]
    except KeyError:
        return False
    else:
        for key in path[1:]:
            try:
                field_type = [field for field in attr.fields(obj) if field.name == key][0].type
            except IndexError:
                return False
            else:
                obj = field_type
                if not attr.has(obj):
                    if key == path[-1]:
                        return True
                    return False


def get_user_data(data: dict) -> UserData:
    """
    Extracts UserData object from any dataclass that contains UserData as a field.

    Parameters:
        - data: Input dict that contains UserData.

    Returns:
        UserData: UserData object contained within the input dataclass.
    """

    if "user" in data.keys():
        user = data["user"]
        pii = UserPersonalData(**user["pii"])
        return UserData(id=user["id"], is_active=user["is_active"], pii=pii)
    
    for key, value in data.items():
        if isinstance(value, dict):
            return get_user_data(value)
    return None


def extract_payload(public_signal_kwargs: dict, as_dict=False) -> dict:
    """
    Extracts the event payload from the event data.

    Parameters:
        - payload: The event data.
        - as_dict: Transform returned dict to primitives.

    Returns:
        dict: The event "cleaned" payload.
    """
    for key, value in public_signal_kwargs.items():
        if attr.has(value):
            return {key: asdict(value)} if as_dict else {key: value}
