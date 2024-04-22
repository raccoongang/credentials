Configuration examples
======================

These examples will put some light on how to configure requirements and data rules for desired use cases.

.. note::

    **Any of the following examples can be combined together for more specific use cases**.

    e.g.: "Course A and Course B completion."

Implemented use cases
----------------------

ANY COURSE completion
~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On any course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``

ANY CCX course completion
~~~~~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.ccx.course.passing.status.updated.v1``
    - description: ``On any CCX course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``

ANY COURSE completion EXCEPT a specific course
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On any course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 2:
    - key path: ``course.course_key``
    - operator: ``not equals``
    - value: ``course-v1:edX+DemoX+Demo_Course``

SPECIFIC COURSE completion
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

MULTIPLE SPECIFIC COURSES completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
- Data rule 3:
    - key path: ``course.course_key``
    - operator: ``equals``
    - value: ``course-v1:edX+DemoX+OTHER_Course``

SPECIFIC CCX course completion
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

ANY CCX course completion ON a SPECIFIC MASTER course
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

ANY CCX course completion ON a SPECIFIC MASTER course EXCEPT a SPECIFIC CCX course
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
- Data rule 3:
    - key path: ``course.ccx_course_key``
    - operator: ``not equals``
    - value: ``ccx-v1:edX+DemoX+Demo_Course+ccx@1``


-----

Future work
-----------

- Event combination alternatives... (e.g. "Logical `OR` rule sets: Course A OR Course B completion");

- Single generic event (e.g. "Email activation", "Profile data completion");
- Repetitive events (e.g. "5 arbitrary course completion");
- Prerequisite events (e.g. "5 specific courses completion in a specified order");
- Time-ranged event (e.g. "Arbitrary course completion during the February 2022");
- Badge dependencies (e.g. "Badge A + Badge B = Badge C");
- Multiple times same badge earning (e.g. "3 arbitrary course completions make badge earned x3");
