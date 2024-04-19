Configuration examples
======================

These examples will put some light on how to configure requirements and data rules for desired use cases.

.. note::

    **Any of the following examples can be combined together for more specific use cases**.

    e.g.: "Course A and Course B completion."

Implemented use cases
----------------------

Any course completion
~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On any course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``

Any CCX course completion
~~~~~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.ccx.course.passing.status.updated.v1``
    - description: ``On any CCX course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``

Specific course completion
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On the Demo course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 2:
    - key path: ``course.course_key``
    - operator: ``equals``
    - value: ``course-v1:edX+DemoX+Demo_Course``

Specific CCX course completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.ccx.course.passing.status.updated.v1``
    - description: ``On the Demo CCX1 course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 2:
    - key path: ``course.ccx_course_key``
    - operator: ``equals``
    - value: ``ccx-v1:edX+DemoX+Demo_Course+ccx@1``

Any CCX course completion for the specific master course
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.ccx.course.passing.status.updated.v1``
    - description: ``On any Demo CCX course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 2:
    - key path: ``course.master_course_key``
    - operator: ``equals``
    - value: ``course-v1:edX+DemoX+Demo_Course``
