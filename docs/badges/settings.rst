Settings
========

Badges feature settings allow configuration:

- feature availability;
- event bus public signals subset for badges;
- the Credly service integration details (URLs, sandbox usage, etc.);


Feature switch
--------------

The Badges feature is under a feature switch (disabled by default).

To enable the feature, update these settings as follows:

.. code-block:: python

    # Platform services settings:
    FEATURES["BADGES_ENABLED"] = True

    # Credentials service settings:
    BADGES_ENABLED = True


Default settings
----------------

The feature has its configuration:

.. code-block:: python

    # Credentials settings:
    BADGES_CONFIG = {
        # these events become available in requirements/penalties setup:
        "events": [
            "org.openedx.learning.course.passing.status.updated.v1",
            "org.openedx.learning.ccx.course.passing.status.updated.v1",
        ],
        "credly": {
            "CREDLY_BASE_URL": "https://credly.com/",
            "CREDLY_API_BASE_URL": "https://api.credly.com/v1/",
            "CREDLY_SANDBOX_BASE_URL": "https://sandbox.credly.com/",
            "CREDLY_SANDBOX_API_BASE_URL": "https://sandbox-api.credly.com/v1/",
            "USE_SANDBOX": False,
        },
    }

- ``events`` - explicit event bus signals list (only events with PII user data in payload are applicable).
- ``credly`` - Credly integration details.

Credly integration
~~~~~~~~~~~~~~~~~~

- USE_SANDBOX - enables Credly sandbox usage (development, testing);
- CREDLY_BASE_URL - Credly service host URL;
- CREDLY_API_BASE_URL - Credly API host URL;
- CREDLY_SANDBOX_BASE_URL - Credly sandbox host URL;
- CREDLY_SANDBOX_API_BASE_URL - Credly sandbox API host URL;


Event bus settings
------------------

    ``learning-badges-lifecycle`` is the event bus topic for all Badges related events.

The Badges feature has updated event bus producer configurations for the Platform and the Credentials services.

Source public signals
~~~~~~~~~~~~~~~~~~~~~

Platform's event bus producer configuration was extended with 2 public signals:

- information about the fact someone's course grade was updated (allows course completion recognition);
- information about the fact someone's CCX course grade was updated (allows CCX course completion recognition);

.. code-block:: python

    # Platform services settings:
    EVENT_BUS_PRODUCER_CONFIG = {
        ...

        "org.openedx.learning.course.passing.status.updated.v1": {
            "learning-badges-lifecycle": {
                "event_key_field": "course_passing_status.course.course_key",
                "enabled": _should_send_learning_badge_events,
            },
        },
        "org.openedx.learning.ccx.course.passing.status.updated.v1": {
            "learning-badges-lifecycle": {
                "event_key_field": "course_passing_status.course.course_key",
                "enabled": _should_send_learning_badge_events,
            },
        },
    }

Emitted public signals
~~~~~~~~~~~~~~~~~~~~~~

The Badges feature introduced 2 own event types:

- information about the fact someone has earned a badge;
- information about the fact someone's badge was revoked;

.. code-block:: python

    # Credentials service settings:
    EVENT_BUS_PRODUCER_CONFIG = {
        ...

        "org.openedx.learning.badge.awarded.v1": {
            "learning-badges-lifecycle": {"event_key_field": "badge.uuid", "enabled": True },
        },
        "org.openedx.learning.badge.revoked.v1": {
            "learning-badges-lifecycle": {"event_key_field": "badge.uuid", "enabled": True },
        },
    }
