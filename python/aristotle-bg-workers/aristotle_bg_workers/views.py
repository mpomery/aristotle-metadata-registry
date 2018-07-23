from django.http.response import HttpResponse, JsonResponse
from django_celery_results.models import TaskResult
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View, ListView, TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin

from aristotle_mdr.utils import fetch_aristotle_settings

from aristotle_bg_workers.models import ExtraTaskInfo
from aristotle_bg_workers.celery import debug_task, app
from aristotle_bg_workers.helpers import store_task, date_convert, get_pretty_name

from aristotle_bg_workers.tasks import reindex_task, loadhelp_task

from django_celery_results.models import TaskResult

class IsSuperUserMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser

class GenericTaskView(IsSuperUserMixin, View):

    def get(self, request, task_name):

        task_promise = app.send_task(task_name)
        display_name = get_pretty_name(task_name)
        store_task(task_promise.id, display_name, request.user)
        return HttpResponse(task_promise.id)


class GetTaskStatusView(View):

    def get(self, request):

        cached_status_list = cache.get('task_status')

        if cached_status_list:
            return JsonResponse({'results': cached_status_list})
        else:

            results_list = []

            # Get most recent 5 tasks
            tasks = TaskResult.objects.all().order_by('-id')[:5]

            for task in tasks:
                try:
                    extra = task.extrainfo
                except ObjectDoesNotExist:
                    extra = None

                # If extra not attached the signal may not have completed
                if not extra:
                    # Query eti directly in this case
                    try:
                        extra = ExtraTaskInfo.objects.get(celery_task_id=task.task_id)
                    except ExtraTaskInfo.DoesNotExist:
                        extra = None

                if extra:
                    name = extra.task_name
                    date_started = date_convert(extra.date_started)
                    task_user = extra.task_creator.full_name
                else:
                    name = 'Unknown'
                    date_started = 'Unknown'
                    task_user = 'Unknown'

                date_done = date_convert(task.date_done)
                if task.status == 'STARTED':
                    date_done = ''

                result = task.result
                if result and task.status != 'STARTED':
                    formatted_result = result.strip('\"').replace("\\n", "<br />")
                else:
                    formatted_result = ""

                results_list.append({
                    'id': task.task_id,
                    'name': name,
                    'status': task.status,
                    'date_done': date_done,
                    'date_started': date_started,
                    'user': task_user,
                    'result': formatted_result
                })

            cache.set('task_status', results_list)

            return JsonResponse({'results': results_list})

class TaskListView(IsSuperUserMixin, ListView):

    model = TaskResult
    template_name = "aristotle_bg_workers/task_history.html"
    paginate_by = 25
    ordering = ['-date_done']

class TaskListLimitedView(TaskListView):
    # Used for display of tasks on cloud dashboard

    template_name = "aristotle_bg_workers/task_list.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'noresult': True})
        return context

class TaskRunnerView(IsSuperUserMixin, TemplateView):

    template_name = "aristotle_bg_workers/task_runner.html"

    def get_context_data(self, **kwargs):

        tasks = ['reindex', 'load_help']
        task_buttons = []
        from aristotle_bg_workers.helpers import get_pretty_name

        for task in tasks:
            task_buttons.append({'display_name': get_pretty_name(task), 'task_name': task})

        kwargs['tasks'] = task_buttons
        return super().get_context_data(**kwargs)
