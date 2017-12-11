from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse

import aristotle_mdr.tests.utils as utils
from aristotle_mdr import models
import datetime

from django.test.utils import setup_test_environment
setup_test_environment()


class UserManagementPages(utils.LoggedInViewPages, TestCase):
    def setUp(self):
        super(UserManagementPages, self).setUp()

    def test_user_cannot_view_userlist(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle-user:registry_user_list',))
        self.assertEqual(response.status_code, 403)

    def test_su_can_view_userlist(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle-user:registry_user_list',))
        self.assertEqual(response.status_code, 200)


    def test_user_cannot_deactivate_user(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle-user:deactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('aristotle-user:deactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 403)

    def test_su_can_deactivate_user(self):
        self.login_superuser()
        self.assertTrue(self.viewer.is_active == True)
        response = self.client.get(reverse('aristotle-user:deactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.viewer.is_active == True)
        response = self.client.post(reverse('aristotle-user:deactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 302)

        self.viewer = get_user_model().objects.get(pk=self.viewer.pk)
        self.assertTrue(self.viewer.is_active == False)

    def test_user_cannot_reactivate_user(self):
        self.login_ramanager()
        self.viewer.is_active = False
        self.viewer.save()

        response = self.client.get(reverse('aristotle-user:reactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('aristotle-user:reactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.viewer.is_active == False)

    def test_su_can_reactivate_user(self):
        self.login_superuser()
        self.viewer.is_active = False
        self.viewer.save()

        response = self.client.get(reverse('aristotle-user:reactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.viewer.is_active == False)
        response = self.client.post(reverse('aristotle-user:reactivate_user', args=[self.viewer.pk]))
        self.assertEqual(response.status_code, 302)

        self.viewer = get_user_model().objects.get(pk=self.viewer.pk)
        self.assertTrue(self.viewer.is_active == True)
