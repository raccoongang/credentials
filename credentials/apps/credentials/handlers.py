from django.dispatch import receiver

from openedx_events.learning.signals import COURSE_GRADE_NOW_FAILED, CCX_COURSE_GRADE_NOW_FAILED

from apps.badges.signals.signals import BADGE_PROGRESS_INCOMPLETE

@receiver(COURSE_GRADE_NOW_FAILED)
def listen_failed_course(sender, *args, **kwargs):
    BADGE_PROGRESS_INCOMPLETE.send(sender=sender, username=kwargs.get("user_course_data").user.username, badge_template_id=...) # find way to get badge_template_id

@receiver(CCX_COURSE_GRADE_NOW_FAILED)
def listen_failed_ccx_course(sender, *args, **kwargs):
    BADGE_PROGRESS_INCOMPLETE.send(sender=sender, username=..., badge_template_id=...) # find way to get username and badge_template_id
