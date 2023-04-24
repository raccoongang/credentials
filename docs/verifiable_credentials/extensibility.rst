Extensibility
=============

Storages
--------

Storage backend classes describe a destination for issued verifiable credentials. Basically, storages are wallets (mobile or web applications). By default, there is a single integration enabled:

- `Learner Credential Wallet`_ (mobile apps: Android, IOS)

Additionally, you can try to install the `openedx-wallet`_ POC for investigation/onboarding purposes.

Data Models
-----------

Data model classes are `DRF`_ serializers which compose verifiable credentials of different specifications.

Credentials data models
~~~~~~~~~~~~~~~~~~~~~~~

There are 2 specifications included by default:

- `Verifiable Credentials Data Model v1.1`_
- `Open Badges Specification v3.0`_

Additional specifications may be implemented as separate `plugins`_.

Credentials status information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
    Status information allows instant checks to figure out if the presented verifiable credential is still valid and actual.

**Status List v2021** is a special kind of verifiable credential. It serves as a mechanism of verification for issued verifiable credentials (meaning, it does not carry achievement information itself but it is a registry of statuses for all created achievement-related verifiable credentials).

- `Verifiable Credential Status List v2021`_

There are 2 parts of the approach:

- status entry (becomes a part of each issued verifiable credential and carries the info "how to check status")
- status list (an Issuer-centric separate freely reachable statuses registry)

Plugins
-------

Both `data models`_ and `storages`_ may be implemented as a Credentials IDA installable pluggable applications. Please, see the `openedx-wallet`_ POC (by the `Raccoon Gang`_) as an example.

.. _Verifiable Credentials Data Model v1.1: https://www.w3.org/TR/vc-data-model-1.1/
.. _Open Badges Specification v3.0: https://1edtech.github.io/openbadges-specification/ob_v3p0.html
.. _Verifiable Credential Status List v2021: https://w3c.github.io/vc-status-list-2021/
.. _data models: extensibility.html#data-models
.. _storages: extensibility.html#storages
.. _plugins: extensibility.html#plugins
.. _openedx-wallet: https://github.com/raccoongang/openedx-wallet
.. _Raccoon Gang : https://raccoongang.com
.. _Learner Credential Wallet: https://lcw.app
.. _DRF: https://www.django-rest-framework.org/