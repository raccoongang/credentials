Implementation Details
======================

Badges feature is implemented as a separate application within the Credentials Open edX service:

.. code-block::

        credentials/apps/badges/

Events (Event Bus)
------------------

        Badges feature always relies on events (public signals) with user data.

New events
~~~~~~~~~~

Badges feature extends the set of already `published events`_ with its own set of new public events:

- `BADGE_AWARDED` (Credentials)
- `BADGE_REVOKED` (Credentials)

In addition to already present `public events`_ Badges also relies on (but event types set may be extended):

- `COURSE_GRADE_NOW_PASSED` (LMS)
- `COURSE_GRADE_NOW_FAILED` (LMS)


Data models
-----------

Badges application maintains a set of data models.

BadgeTemplate
~~~~~~~~~~~~~



Requirement
~~~~~~~~~~~

**Requirement** describes an association between a BadgeTemplate and an Event.

It carries *Rules*: **which** event, **how** and **when** must occur.
Badge can have multiple Requirements.

.. code-block:: python

        Requirement:
        """
        Defines a single rule for a badge type.
        """
        - BadgeTemplate (relation)
        - event_type (event identifier)

        - times <int> default=1 (allows repetitive events)
        - start <timestamp> optional (allows time range events)
        - end <timestamp> optional (allows time range events)
        - rule_set: <int> default=1 (allows requirements combination)

Fulfillment
~~~~~~~~~~~

**Fulfillment** record is associated with a Learner. It tracks a single Requirement fulfillment for given learner.

.. code-block:: python

        Fulfillment:
        """
        Tracks rule fulfillment for user.
        """
        - Requirement (relation)
        - username: <username>
        - times: <int>
        - completed <bool>

UserCredential
~~~~~~~~~~~~~~

Earned badges are `UserCredential` records with a generic relation to the `BadgeTemplate`.

Badges extend currently present:
        - program certificates
        - course certificates

.. code-block:: python

        UserCredential:
        """
        Earned badge.
        """
        ...
        - uuid
        - username: <username>
        - status: "awarded" | "revoked"
        ...


Badge Processor
---------------

**BadgeProcessor** (BP) is an entity which is responsible for incoming public events processing.

- `BadgeProcessor` class is inherited from the `BaseProcessor` which provides expected interface.
- `BadgeProcessor` is auto-registered as a receiver for all configured event types.

Event processing pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~

For received Event:

- active badge templates set identification;
- relevant requirements identification;
- requirements restrictions checks (e.g. time range, not yet implemented);
- requirements effect application - corresponding fulfillments update for the given user;

        `Badge Processor` doesn't bother about user's badging progress, since it is the main responsibility of the `Badge Collector`.

.. note::
        `Distribution backends`_ should be able to override processing implementation.

Badge Collector
---------------

**BadgeCollector** (BC) is an entity which is responsible for users badging progress tracking, as well as for awarding of already completed badges.

- `BadgeCollector` class is inherited from the `BaseCollector` which provides expected interface.
- `BadgeCollector` is registered as a receiver for Fulfillment records.

Badge Collector is subscribed for `Fulfillment` records updates.

Badge collecting pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~

For updated requirement Fulfillment:

- `award` effect
        - single requirement fulfillment evaluation (completion flag is set)
        - related requirements fulfillment evaluation (completion flag is set)
        - badge completion evaluation
        - completed badge awarding (UserCredential is created)
- `revoke` effect
        - single requirement fulfillment revocation (completion flag is reset)
        - completed badge revocation (UserCredential status="revoked")

Feature sequence diagrams
-------------------------

See `Credly backend examples`_.

.. _published events: /event_bus.html#events-published
.. _public events: /event_bus.html#events-consumed
.. _Distribution backends: distribution.html
.. _Credly backend examples: distribution.html#more-details