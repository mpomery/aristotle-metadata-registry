from django.test import TestCase

import aristotle_mdr.tests.utils as utils
from aristotle_mdr.models import ObjectClass, Workgroup
from django.core.urlresolvers import reverse

from django.test.utils import setup_test_environment
setup_test_environment()


class TestBulkActions(utils.LoggedInViewPages, TestCase):
    def setUp(self):
        super(TestBulkActions, self).setUp()
        self.item = ObjectClass.objects.create(
            name="Test Object",
            workgroup=self.wg1,
        )
        self.su.profile.favourites.add(self.item)

    def test_incomplete_action_exists(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle:userFavourites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incomplete action')
