from django.urls import reverse
from django.test import TestCase

from aristotle_mdr.tests import utils
from aristotle_mdr.utils import setup_aristotle_test_environment

setup_aristotle_test_environment()


class TestGenericPagesLoad(utils.LoggedInViewPages, TestCase):

    def test_anon_cant_use_generic(self):
        from extension_test.models import Questionnaire
        from aristotle_mdr.models import Workgroup

        wg = Workgroup.objects.create(name="Setup WG")
        q = Questionnaire.objects.create(name='test questionnaire', workgroup=wg)
        url = reverse('extension_test:questionnaire_add_question', kwargs={'iid': q.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('friendly_login') + "?next=" + url)
