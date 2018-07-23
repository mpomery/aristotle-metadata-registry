from django.core.cache import cache
from aristotle_bg_workers.models import ExtraTaskInfo
from django_celery_results.models import TaskResult

# Helper functions
import logging
logger = logging.getLogger(__name__)

# Store task in the list as running
def store_task(task_id, name, user):

    eti = ExtraTaskInfo(
        task_name=name,
        task_creator=user
    )

    tr = TaskResult.objects.filter(task_id=task_id)
    if (tr.count() > 0):
        # If a result already exists then attach the eti
        task_result = tr[0]
        eti.task = tr[0]
        eti.save()
    else:
        eti.celery_task_id = task_id
        eti.save()

def date_convert(date):
    return date.strftime('%d/%m/%y %I:%M %p')

def get_pretty_name(name):
    return name.title().replace('_', ' ')
