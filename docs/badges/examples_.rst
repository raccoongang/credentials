Configuration examples
======================

These examples will put some light on how to configure requirements and data rules for desired use cases.

Implemented use cases
----------------------

Any course completion
~~~~~~~~~~~~~~~~~~~~~

- Requirement 1:
    - event type: ``org.openedx.learning.course.passing.status.updated.v1``
    - description: ``On the Demo course completion.``
- Data rule 1:
    - key path: ``status``
    - operator: ``equals``
    - value: ``passing``

Any CCX course completion
~~~~~~~~~~~~~~~~~~~~~~~~~

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

Any CCX course completion for specific master course
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~






Roadmap use cases
-----------------

- Single generic event (e.g. "Email activation", "Profile data completion");
- Repetitive events (e.g. "5 arbitrary courses completions");
- Events combination (e.g. "5 specific courses completions")
- Prerequisite events (e.g. "5 specific courses completions in defined order");
- Time-ranged event (e.g. "Arbitrary course completion during January 2024");
- Badge dependencies (e.g. "Badge A + Badge B = Badge C");
- Multiple times same badge earning (e.g. "3 arbitrary course completions make badge earned x3");
- Event combination alternatives... (e.g. "Logical `OR` rule sets: Course A OR Course B completion");