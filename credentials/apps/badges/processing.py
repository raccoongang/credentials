"""
Badge templates progress evaluation.
"""

from openedx_events.learning.data import BadgeData, BadgeTemplateData
from openedx_events.learning.signals import BADGE_AWARDED, BADGE_REVOKED

from .models import BadgeTemplate


def process(signal, sender, **kwargs):
    """
    Processes incoming public signal consumed from event bus and re-emitted within the service.
    """

    # find all REQUIREMENTs for the signal;
    #   if no requirements - drop (signal is not used);
    # personalize: associate signal's USER (event "author");
    #   if not identified - drop (no user info?);
    # check each relevant requirement:
    #   if the REQUIREMENT is already fulfilled for USER - drop;
    #   if data rules attached - apply each rule:
    #       try traverse deep key - if not exists - drop;
    #       get expected value (TODO: allow empty strings?)
    #       apply operator (default: string comparison)

    # signal processing drop == StopEventProcessingException(reason=NO_REQUIREMENTS)
    # requirement processing drop == StopRequirementProcessingException(reason=CANNOT_PERSONALIZE | DATA_ATTR_NOT_FOUND...)

    # FIXME: this is a temporary solution for testing purposes
    badge_template = BadgeTemplate.objects.last()
    badge_data = BadgeData(
        uuid="badge-uuid",
        user=kwargs.get("user_course_data").user,
        template=BadgeTemplateData(
            uuid=str(badge_template.uuid),
            type=badge_template.origin,
            name=badge_template.name,
            description=badge_template.description,
            image_url=badge_template.icon.url,
        ),
    )

    if sender == "org.openedx.learning.course.grade.now.passed.v1":
        BADGE_AWARDED.send_event(badge=badge_data)
    elif sender == "org.openedx.learning.course.grade.now.failed.v1":
        BADGE_REVOKED.send_event(badge=badge_data)


def collect(sender, **kwargs):
    """ """
    pass


# TODO: use cases
# 1. Active Badge Template configuration updates (forbid active badge templates changes!)
