from django.test import TestCase, tag, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from unittest.mock import patch, MagicMock

import aristotle_mdr.tests.utils as utils

from aristotle_mdr.utils import setup_aristotle_test_environment

setup_aristotle_test_environment()


class UserManagementPages(utils.LoggedInViewPages, TestCase):
    def setUp(self):
        super().setUp()

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

    def test_send_invitation(self):

        self.login_superuser()

        response = self.client.get(reverse('aristotle-user:registry_invitations_create'))
        self.assertEqual(response.status_code, 200)

        # Test mail outbox empty
        self.assertEqual(len(mail.outbox), 0)

        data = {
            'email_list': 'wow@example.com\nmetoo@example.com'
        }

        post_response = self.client.post(reverse('aristotle-user:registry_invitations_create'), data)
        self.assertEqual(post_response.status_code, 302)

        # Test that invitations were sent
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(mail.outbox[0].subject.startswith('You\'ve been invited'))

    def test_accept_invitation(self):

        self.login_superuser()
        self.assertEqual(len(mail.outbox), 0)

        data = {
            'email_list': 'test@example.com'
        }

        post_response = self.client.post(reverse('aristotle-user:registry_invitations_create'), data)
        self.assertEqual(post_response.status_code, 302)

        # Test that invitations were sent
        self.assertEqual(len(mail.outbox), 1)

        self.logout()
        message = mail.outbox[0].body
        start = message.find('/account/')
        end = message.find('\n', start)

        accept_url = message[start:end]

        accept_response = self.client.get(accept_url)

        self.assertEqual(accept_response.status_code, 200)

        formfields = accept_response.context['form'].fields.keys()
        removed_fields = ['username', 'first_name', 'last_name']
        added_fields = ['short_name', 'full_name']

        for field in removed_fields:
            self.assertFalse(field in formfields)

        for field in added_fields:
            self.assertTrue(field in formfields)

        accept_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'short_name': 'Test',
            'password': 'verynice',
            'password_confirm': 'verynice'
        }

        response = self.client.post(accept_url, accept_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr/friendly_login.html')
        self.assertTrue('welcome' in response.context.keys())

        new_user = get_user_model().objects.get(email='test@example.com')
        self.assertTrue(new_user.is_active)
        self.assertTrue(new_user.password)
        self.assertEqual(new_user.short_name, 'Test')
        self.assertEqual(new_user.full_name, 'Test User')

    @tag('runthis')
    def test_send_registration_invite(self):

        self.logout()

        mock_settings = MagicMock(return_value={'registry': {'self_signup_enabled': False}})
        with patch('aristotle_mdr.contrib.user_management.org_backends.fetch_aristotle_settings', mock_settings):
            response = self.client.get(reverse('aristotle-user:signup_register'))
            self.assertEqual(response.status_code, 200)
            self.assertFalse('form' in response.context)
            self.assertTrue('message' in response.context)

        response = self.client.get(reverse('aristotle-user:signup_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

        #post_response = self.client.post('aristotle-user:signup_register', {'email', 'aintnuffin@example.com'})


