from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.management import call_command

from celery.utils.log import get_task_logger
from io import StringIO

logger = get_task_logger(__name__)


def run_django_command(cmd, *args, **kwargs):
    err = StringIO()
    out = StringIO()
    call_command(cmd, stdout=out, stderr=err, **kwargs)
    err.seek(0)
    out.seek(0)
    message = (
"""Result:

{out}

Errors:

{err}
"""
).format(
    err=str(err.read()) or "None",
    out=str(out.read())
)
    logger.debug(message)
    return message


@shared_task(name='reindex')
def reindex_task():
    return run_django_command('rebuild_index', interactive=False)


@shared_task(name='load_help')
def loadhelp_task():

    return run_django_command('load_aristotle_help')
