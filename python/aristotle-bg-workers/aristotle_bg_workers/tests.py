from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from unittest.mock import patch

from django_celery_results.models import TaskResult
from aristotle_bg_workers.models import ExtraTaskInfo

from aristotle_bg_workers.helpers import store_task
import json

@override_settings(SECURE_SSL_REDIRECT=False)
class BackgroundTaskTestCase(TestCase):

    # These unit tests do not require a worker or broker to be running
    # As such this doesnt test celery integration

    def store_taskresult(self, id, name, user, status='SUCCESS'):
        store_task(id, name, user)

        tr = TaskResult.objects.create(
            task_id=id,
            status=status
        )
        return tr

    def get_results_list(self):
        response = self.client.get(reverse('aristotle_bg_workers:dbstatus'))
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        results_list = json_content['results']
        return results_list

    def test_load_worker_run(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle_bg_workers:run_task'))
        tasks_list = response.context['tasks']
        self.assertNotEqual(tasks_list, [])

        flat_list = []
        for task in tasks_list:
            flat_list.append(task['task_name'])

        self.assertTrue('reindex' in flat_list)
        self.assertTrue('load_help' in flat_list)

        self.assertEqual(response.status_code, 200)

    @patch('aristotle_bg_workers.views.app.send_task')
    @patch('aristotle_bg_workers.views.store_task')
    def test_task_start(self, helper, reindex_task):
        # Have to mock from views since helpers has already been imported

        response = self.client.get(reverse('aristotle_bg_workers:starttask', kwargs={'task_name': 'reindex'}))
        self.assertEqual(response.status_code, 302)

        self.login_superuser()

        response = self.client.get(reverse('aristotle_bg_workers:starttask', kwargs={'task_name': 'reindex'}))
        self.assertEqual(response.status_code, 200)

        reindex_task.assert_called_once_with('reindex')
        self.assertTrue(helper.called)

    def test_store_task(self):

        # Tests the store_task helper function
        store_task('12345', 'Test Task', self.su)

        eti = ExtraTaskInfo.objects.get(celery_task_id="12345")

        self.assertEqual(eti.task_name, 'Test Task')
        self.assertEqual(eti.task_creator, self.su)

    def test_extra_info_stored(self):

        tr = self.store_taskresult('123-456-789', 'Test Task', self.su)

        self.assertEqual(tr.extrainfo.task_name, 'Test Task')
        self.assertEqual(tr.extrainfo.task_creator, self.su)

    def test_extra_info_stored_reverse(self):
        # Test if they are attached if task result stored first

        tr = TaskResult.objects.create(
            task_id='222-222',
            status='STARTED'
        )

        store_task('222-222', 'Reverse Test Task', self.su)

        new_tr = TaskResult.objects.get(task_id='222-222')
        self.assertEqual(new_tr.extrainfo.task_name, 'Reverse Test Task')
        self.assertEqual(new_tr.extrainfo.task_creator, self.su)

    def test_task_status(self):

        # Create task results
        self.store_taskresult('123', 'Test Task', self.su)
        self.store_taskresult('456', 'Test Task', self.su)
        # Store one with no ExtraTaskInfo object attached
        tr = TaskResult.objects.create(
            task_id='789',
            status='SUCCESS'
        )

        # Check status
        results_list = self.get_results_list()

        for result in results_list:
            idknown = result['id'] in ['123', '456', '789']
            self.assertTrue(idknown)
            if result['id'] in ['123', '456']:
                self.assertEqual(result['name'], 'Test Task')
                self.assertNotEqual(result['date_started'], 'Unknown')
            elif result['id'] == '789':
                self.assertEqual(result['name'], 'Unknown')
                self.assertEqual(result['date_started'], 'Unknown')

    def test_task_status_started(self):

        # Store task results with one started
        self.store_taskresult('123', 'Test Task', self.su)
        self.store_taskresult('456', 'Test Task', self.su, status='STARTED')

        # Check status
        results_list = self.get_results_list()

        # Check that date done isnt returned when the task has not been completed
        for result in results_list:
            if result['status'] == 'STARTED':
                self.assertEqual(result['date_done'], '')
            else:
                self.assertNotEqual(result['date_done'], '')

    def test_task_status_order(self):

        # Create task results
        self.store_taskresult('123', 'Test Task', self.su)
        self.store_taskresult('456', 'Test Task', self.su)

        # Check status
        results_list = self.get_results_list()

        # Check results are in correct order (most recent first)
        self.assertEqual(results_list[0]['id'], '456')
        self.assertEqual(results_list[1]['id'], '123')

    def test_task_status_cache(self):

        # Create task results
        tr = self.store_taskresult('123', 'Test Task', self.su, status='STARTED')

        results_list = self.get_results_list()
        self.assertEqual(results_list[0]['name'], 'Test Task')
        self.assertEqual(results_list[0]['status'], 'STARTED')

        cached_results = cache.get('task_status')
        cached_results[0]['name'] = 'Cached Name'
        cache.set('task_status', cached_results)

        # Test if we are loading from cache
        results_list = self.get_results_list()
        self.assertEqual(results_list[0]['name'], 'Cached Name')
        self.assertEqual(results_list[0]['status'], 'STARTED')

        # Test if cache was deleted on save
        tr.status = 'SUCCESS'
        tr.save()
        results_list = self.get_results_list()
        self.assertEqual(results_list[0]['name'], 'Test Task')
        self.assertEqual(results_list[0]['status'], 'SUCCESS')

    def test_save_result_no_task_cache(self):

        cache.delete('tasks')
        tr = TaskResult.objects.create(
            task_id='123',
            status='SUCCESS'
        )

        with self.assertRaises(ObjectDoesNotExist):
            extra = tr.extrainfo

    def test_updating_result_no_task_cache(self):

        cache.delete('tasks')
        tr = TaskResult.objects.create(
            task_id='123',
            status='STARTED'
        )
        tr.status = 'SUCCESS'
        tr.save()

        with self.assertRaises(ObjectDoesNotExist):
            extra = tr.extrainfo

    @patch('aristotle_bg_workers.messages.task_completed')
    @patch('aristotle_bg_workers.messages.task_failed')
    def test_notification_functions_called(self, task_failed, task_completed):

        tr = self.store_taskresult('123', 'Test Task', self.su, status='STARTED')
        tr.status = 'SUCCESS'
        tr.save()

        task_completed.assert_called_once_with(self.su, tr.extrainfo)

        tr.status = 'FAILURE'
        tr.save()

        task_failed.assert_called_once_with(self.su, tr.extrainfo)

    def test_notifications_created(self):

        self.assertEqual(self.su.notifications.all().count(), 0)

        tr = self.store_taskresult('123', 'Test Task', self.su, status='STARTED')
        tr.status = 'SUCCESS'
        tr.save()

        self.assertEqual(self.su.notifications.all().count(), 1)

        notif = self.su.notifications.first()
        self.assertTrue('A task has been completed' in notif.verb)
        self.assertTrue(isinstance(notif.target, ExtraTaskInfo))

        tr.status = 'FAILURE'
        tr.save()

        self.assertEqual(self.su.notifications.all().count(), 2)

        notif = self.su.notifications.first()
        self.assertTrue('A task has failed' in notif.verb)
        self.assertTrue(isinstance(notif.target, ExtraTaskInfo))
