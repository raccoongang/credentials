Configuration
=============

Verifiable Credentials feature is optional. It is disabled by default.

The feature introduces its own set of default settings which are namespaced in the VERIFIABLE_CREDENTIALS setting, like this:

.. code-block:: python

    VERIFIABLE_CREDENTIALS = {
        'setting_1': 'value_1',
        'setting_2': 'value_2',
    }

.. code-block:: python

    # verifiable_credentials/settings.py

    DEFAULTS = {
        "DEFAULT_DATA_MODELS": [
            "credentials.apps.verifiable_credentials.composition.verifiable_credentials.VerifiableCredentialsDataModel",
            "credentials.apps.verifiable_credentials.composition.open_badges.OpenBadgesDataModel",
        ],
        "DEFAULT_STORAGES": [
            "credentials.apps.verifiable_credentials.storages.learner_credential_wallet.LCWallet",
        ],
        "DEFAULT_ISSUER": {
            "ID": "generate-me-with-didkit-lib",
            "KEY": "generate-me-with-didkit-lib",
            "NAME": "Default (system-wide)",
        },
        "DEFAULT_ISSUANCE_REQUEST_SERIALIZER": "credentials.apps.verifiable_credentials.issuance.serializers.IssuanceLineSerializer",
        "DEFAULT_RENDERER": "credentials.apps.verifiable_credentials.issuance.renderers.JSONLDRenderer",
        "STATUS_LIST_STORAGE": "credentials.apps.verifiable_credentials.storages.status_list.StatusList2021",
        "STATUS_LIST_DATA_MODEL": "credentials.apps.verifiable_credentials.composition.status_list.StatusListDataModel",
        "STATUS_LIST_LENGTH": 10000,
    }

Default data models
-------------------

Deployment configuration can override `data models set`_ with the respect of the following restrictions:

- there always must be at least 1 data model available
- each storage is pre-configured to use some data model which must be available

Default storages
----------------

Deployment configuration can override `storages set`_ with the respect of the following restrictions:

- there always must be at least 1 storage available


Default issuer
--------------

.. note::
    Currently, there is only a single active issuer (system-wide) available So, all verifiable credentials are created (issued) on behalf of this Issuer.

There is the `Issuance Configuration`_ database model, which initial record is created based on these settings.

NAME
~~~~

Verbose issuer name (it is placed into each verifiable credential).

KEY
~~~

A private secret key (JWK) which is used for verifiable credentials issuance (proof/digital signature generation). It can be generated with the help of the `didkit`_ Python (Rust) library.

ID
~~

A unique issuer decentralized identifier (created from a private key, `example`_)

Status List configuration
-------------------------

Length
~~~~~~

``STATUS_LIST_LENGTH`` - default = 10000 (16KB)

Possibly, the only status list settings to configure. A status sequence positions count (how many issued verifiable credentials statuses are included). See `related specs`_ for details.

Storage
~~~~~~~

``STATUS_LIST_STORAGE``

A technical storage class (allows status list implementation override).

Data model
~~~~~~~~~~

``STATUS_LIST_DATA_MODEL``

A data model class (allows status list implementation override).


Other settings are available for advanced tweaks but usually are not meant to be configured:

- Default issuance request serializer (incoming issuance request parsing)
- Default renderer (outgoing verifiable credential presentation)

.. _data models set: extensibility.html#data-models
.. _storages set: extensibility.html#storages
.. _didkit: https://pypi.org/project/didkit/
.. _example: https://github.com/spruceid/didkit-python/blob/main/examples/python_django/didkit_django/issue_credential.py#L12
.. _related specs : https://w3c.github.io/vc-status-list-2021/#revocation-bitstring-length
.. _Issuance Configuration: components.html#administration-site