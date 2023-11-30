Processing
==========

**Processing** is a process of:

- Open edX `public signals` subscription
- badge template requirements analysis
- badge fulfillments update

.. note::
    Events async processing happens in a separate specific (out of the standard Django request-response flow) worker process.
    See EventBus documentation for details.

Events subscription
-------------------

`Feature configuration`_ provides an exclusive list of processed events.
`Badge Processor`_ is auto-connected to listen to those event types.

All registered events are expected to carry user data. In addition, different event types include their specific data set which can be used for `badge requirements`_ specification.

    External async events are retranslated as internal Credentials (standard Django) signals, so registered receivers can process it.

Requirements analysis
---------------------

Once `Event` received, `Badge Processor`_ runs its processing pipeline.
As a result a relevant requirements set for a specific event type is formed.

Fulfillments update
---------------------

Once event-related requirements set is clear, Processor updates/creates corresponding `Fulfillments`_'s attributes for the event-learner.

.. _public events: https://github.com/openedx/openedx-events/blob/main/openedx_events/tooling.py
.. _Feature configuration: configuration.html#feature-configuration
.. _badge requirements: configuration.html#requirements-setup
.. _Badge Processor: details.html#badge-processor
.. _Fulfillments: details.html#fulfillment