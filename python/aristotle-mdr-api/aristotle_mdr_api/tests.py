from django.test import TestCase, Client, override_settings
from django.urls import reverse

from aristotle_mdr.tests import utils

@override_settings(SECURE_SSL_REDIRECT=False)
class TokenTestCase(utils.LoggedInViewPages, TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_create_token(self):

        response = self.client.get(reverse('token_create'))
        self.assertEqual(response.status_code, 302)

        self.login_viewer()

        response = self.client.get(reverse('token_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token_create.html')
