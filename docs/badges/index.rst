Badges (DRAFT)
==============

    **Badges** are an another kind of **credentials**.


Badges feature is briefly described by the following items:

- System allows `badge templates management`_.
- Each badge must be configured with its `requirements`_.
- System `analyzes`_ user-specific events and controls badge requirements `fulfillment`_ by learners.
- On `badge completion`_ learners are awarded the badge.
- Earned badges are `collected`_ for learners within Credentials service.
- System allows `badges distribution`_ to external services via pluggable backends.

----

.. toctree::
    :maxdepth: 1

    quickstart
    configuration
    processing
    collecting
    distribution
    details

.. _badge templates management: configuration.html#badge-templates-management
.. _requirements: configuration.html#requirements-setup
.. _analyzes: processing.html
.. _fulfillment: processing.html
.. _badge completion: processing.html
.. _collected: collecting.html
.. _relevant API endpoints: data.html
.. _badges distribution: distribution.html