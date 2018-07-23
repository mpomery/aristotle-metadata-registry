from django.db.models.signals import pre_save, post_save
from django.core.cache import cache
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from aristotle_bg_workers.models import ExtraTaskInfo
from django_celery_results.models import TaskResult

from aristotle_bg_workers import messages

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=TaskResult)
def task_result_save_callback(sender, instance, created, **kwargs):

    # Delete status cache
    cache.delete('task_status')

    # Get extra task info mapping to task_id
    try:
        extrainfo = instance.extrainfo
    except ObjectDoesNotExist:
        extrainfo = None

    if not extrainfo:

        # Attempt to get ExtraTaskInfo
        try:
            eti = ExtraTaskInfo.objects.get(celery_task_id=instance.task_id)
        except ExtraTaskInfo.DoesNotExist:
            eti = None

        # Link to newly created task
        if eti:
            eti.task = instance
            eti.celery_task_id = None
            eti.save()

    if (created == False) and extrainfo:
        # If not newly created and there is an attached ExtraTaskInfo

        if instance.status == "SUCCESS":
            messages.task_completed(extrainfo.task_creator, extrainfo)

        elif instance.status == "FAILURE":
            messages.task_failed(extrainfo.task_creator, extrainfo)
