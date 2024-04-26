Configuration examples
======================

These examples will put some light on how to configure requirements and data rules for desired use cases.

.. note::

    **Any of the following examples can be combined together for more specific use cases**.


Implemented use cases
----------------------

ANY COURSE GRADE update
~~~~~~~~~~~~~~~~~~~~~~~

    Not that useful. Any interaction with gradable block in any course leads to a badge.

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On any grade update.``

ANY COURSE completion
~~~~~~~~~~~~~~~~~~~~~

    Requires **passing grade** for any course.

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On any course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``

ANY CCX course completion
~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires **passing grade** for any CCX course.

- Requirement 1:
    - event type: ``org.openedx.learning.ccx.course.passing.status.updated.v1``
    - description: ``On any CCX course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``

ANY COURSE completion EXCEPT a specific course
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires **passing grade** for any course excluding the "Demo" course.

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On any course completion, but not the "Demo" course.``
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

    Requires **passing grade** for exact course ("Demo" course).

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

    All specified courses must be completed.

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On the "Demo" course AND "Other" course completion.``
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

    Requires **passing grade** for exact CCX course ("Demo CCX1" course).

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

    Requires **passing grade** for any "child" CCX course that based on the master "Demo" course.

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

    Complicated. Requires **passing grade** for any "child" CCX course that based on the master "Demo" course, excluding the "Demo CCX2" course.

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
    - value: ``ccx-v1:edX+DemoX+Demo_Course+ccx@2``

ONE OF MULTIPLE SPECIFIC COURSES completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A single from specified courses must be completed. Grouped rules are processed as "ANY FROM A GROUP".

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On the "Demo" course OR "Other" course completion.``
    - group: ``unique-group-identifier``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 2:
    - key path: ``course.course_key``
    - operator: ``equals``
    - value: ``course-v1:edX+DemoX+Demo_Course``

- Requirement 2:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On the "Demo" course OR "Other" course completion.``
    - group: ``unique-group-identifier``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 2:
    - key path: ``course.course_key``
    - operator: ``equals``
    - value: ``course-v1:edX+DemoX+OTHER_Course``


SPECIFIC MASTER course OR ANY of its CCX courses EXCEPT a SPECIFIC CCX course completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Here **group = demo** is used to group rules 2 and 3, so any of them lead to a badge.

- Requirement 1:
    - event type: ``org.openedx.learning.ccx.course.passing.status.updated.v1``
    - description: ``On the "Demo" course completion OR...``
    - group: ``demo``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 2:
    - key path: ``course.course_key``
    - operator: ``equals``
    - value: ``course-v1:edX+DemoX+Demo_Course``

- Requirement 2:
    - event type: ``org.openedx.learning.ccx.course.passing.status.updated.v1``
    - description: ``...On any Demo CCX courses completion EXCLUDING CCX3.``
    - group: ``demo``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``
- Data rule 3:
    - key path: ``course.master_course_key``
    - operator: ``equals``
    - value: ``course-v1:edX+DemoX+Demo_Course``
- Data rule 4:
    - key path: ``course.ccx_course_key``
    - operator: ``not equals``
    - value: ``ccx-v1:edX+DemoX+Demo_Course+ccx@3``

-----

Future work
-----------

- Events set extension (e.g. "Email activation", "Profile data completion", "Course section completion", ...);
- Repetitive events (e.g. "5 arbitrary courses completion");
- Prerequisite events (e.g. "5 specific courses completion in a specified order");
- Time-ranged event (e.g. "Arbitrary course completion during the February 2022");
- Badge dependencies (e.g. "Badge A + Badge B = Badge C");
- Multiple times same badge earning (e.g. "3 arbitrary course completions make badge earned x3");
