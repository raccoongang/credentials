from django.dispatch import receiver

from openedx_events.learning.signals import COURSE_GRADE_NOW_PASSED, CCX_COURSE_GRADE_NOW_PASSED

from apps.badges.signals.signals import BADGE_PROGRESS_COMPLETE

@receiver(COURSE_GRADE_NOW_PASSED)
def listen_passed_course(sender, *args, **kwargs):
    BADGE_PROGRESS_COMPLETE.send(sender=sender, username=kwargs.get("user_course_data").user.username, badge_template_id=1)  # temporarily faked badge_template_id

@receiver(CCX_COURSE_GRADE_NOW_PASSED)
def listen_passed_ccx_course(sender, *args, **kwargs):
    BADGE_PROGRESS_COMPLETE.send(sender=sender, username='edx', badge_template_id=1)  # temporarily faked badge_template_id and username
