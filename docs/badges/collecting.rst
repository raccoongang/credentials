Collecting
==========

**Collecting** is a process of:

- learners' `fulfillments` update subscription
- badge requirements fulfillment/revocation analysis
- completed badge awarding
- badge revocation

Fulfillments subscription
-------------------------

Configured `Badge Collector`_ is auto-subscribed for any updates in `Fulfillment`_ records.


Badge completion analysis
-------------------------

- Once user's `Fulfillment`_ is updated, Collector tries to figure out if this progress update made the related Requirement to be **fulfilled**.
- Collector emits `BADGE_REQUIREMENT_FULFILLED` signal.
- If so, Collector goes further and checks all related requirements (if any).
- If all requirements for given badge template are fulfilled, there are no obstacles to award the badge, so Collector emits internal `BADGE_REQUIREMENTS_COMPLETE` signal.


Badge awarding
--------------

On `BADGE_REQUIREMENTS_COMPLETE` signal:

- awarding handler creates new `UserCredential`_ record;
- external event about a badge awarding fact is emitted;


Badge revocation analysis
-------------------------

This is an alternative (reverse) pipeline step for requirements analysis with `revoke` effect set.

- User's `Fulfillment`_ may be updated, so related Requirement stops being fulfilled.
- Related badge template requirements become not fulfilled, so Collector emits internal `BADGE_REQUIREMENTS_NOT_COMPLETE` signal.

Badge revocation
----------------

On `BADGE_REQUIREMENTS_NOT_COMPLETE` signal:

- revocation handler updates `UserCredential`_ record's status to `revoked`;
- external event about the badge revocation fact is emitted;

.. _Badge Processor: details.html#badge-processor
.. _Badge Collector: details.html#badge-collector
.. _Fulfillment: details.html#fulfillment
.. _UserCredential: details.html#usercredential