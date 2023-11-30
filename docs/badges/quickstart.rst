Quick Start
===========

    Learners *earn* badges based on Open edX platform activity.

1. Enable feature
-----------------

Badges feature is optional and it is disabled by default.
So, it must be enabled to be accessible.

.. code-block::

    # Credentials service:
    ENABLE_BADGES = true

2. Validate configuration
-------------------------

Learners' activity is expressed through `system events`_.
Credentials Badges has an explicit `configuration`_ for:

- **consumed (incoming) events** - these events are a basis for **badging rules**;
- **produced (outgoing) events** - these events inform other services about **badging progress**;

Possibly, one will want to extend incoming event types.

3. Create your badge templates
------------------------------

A Badge has its `life-cycle`_ which starts from a template `creation`_.
Newly created badge templates are inactive, since they are not configured.

.. note::
    Badges `distribution backends`_ may extend standard badges management capabilities.

4. Setup badge requirements
---------------------------

The most important part of a badge template configuration is `requirements specification`_. In short, at least one requirement must be associated with a template.

    Requirements describe what must be done before one can get a badge.

Badge template requirements control how badge completion is fulfilled (see currently `available use cases`_)

Additionally, requirement can be configured with `revocation effect`_.

5. Activate configured badge templates
--------------------------------------

Once badge requirements are configured, to make badge available for users one have to "enable" it - put in active state.

Active badges start being taking into account by the `Badge Processor`_.

6. Badge templates maintenance
------------------------------

Badge processing can be "paused" by putting its template to `inactive` state. Inactive state allows badge template editing.

7. Badge template withdrawal
----------------------------

Badge template can be retired by putting it in `archived` state. Such badge templates are not processed anymore.

---


.. _system events: details.html#events-event-bus
.. _configuration: configuration.html#feature-configuration
.. _life-cycle: configuration.html#badges-management
.. _creation: configuration.html#creation
.. _requirements specification: configuration.html#requirements-setup
.. _available use cases: configuration.html#use-cases
.. _revocation effect: configuration.html#revocation-setup
.. _Badge Processor: processing.html#badge-processor
.. _distribution backends: distribution.html