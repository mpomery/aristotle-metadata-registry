from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.test.utils import setup_test_environment
from django.utils import timezone

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
from aristotle_mdr.utils import url_slugify_concept

setup_test_environment()
from aristotle_mdr.tests import utils
import datetime


class LoggedInAutocompletes(utils.LoggedInViewPages, TestCase):
    defaults = {}

    def test_concept_autocompletes(self):
        self.logout()

        item1 = models.ObjectClass.objects.create(name="Test Item 1 (visible to tested viewers)",definition="my definition",workgroup=self.wg1,**self.defaults)
        item2 = models.ObjectClass.objects.create(name="Test Item 2 (NOT visible to tested viewers)",definition="my definition",workgroup=self.wg2,**self.defaults)

        response = self.client.get(
            reverse("aristotle-autocomplete:concept")
        )

        data = utils.get_json_from_response(response)
        self.assertEqual(len(data['results']), 0)

        self.login_superuser()
        response = self.client.get(
            reverse("aristotle-autocomplete:concept")
        )
        data = utils.get_json_from_response(response)
        self.assertEqual(len(data['results']), 2)

        response = self.client.get(
            reverse("aristotle-autocomplete:concept") + "?q=Not"  # Test case insensitivity
        )
        data = utils.get_json_from_response(response)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], item2.id)
