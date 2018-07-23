from django.db import models
from django_celery_results.models import TaskResult
from django.conf import settings
from django.urls import reverse

class ExtraTaskInfo(models.Model):

    class Meta:
        app_label='aristotle_bg_workers'

    task = models.OneToOneField(
        TaskResult,
        on_delete=models.CASCADE,
        related_name='extrainfo',
        null=True,
        blank=True
    )
    task_name = models.CharField(max_length=100)
    task_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    date_started = models.DateTimeField(auto_now_add=True)
    celery_task_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def get_absolute_url(self):
        return reverse('aristotle_mdr:smart_root')

    def __str__(self):
        return self.task_name
