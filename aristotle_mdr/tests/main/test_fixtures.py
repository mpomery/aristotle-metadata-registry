from django.conf import settings
from django.urls import reverse
from django.test import TestCase, override_settings, modify_settings

from django.core.management import call_command
from aristotle_mdr.contrib.help import models

from aristotle_mdr.utils import setup_aristotle_test_environment


setup_aristotle_test_environment()


class TestFixtures(TestCase):
    def test_fixtures(self):
        call_command('loaddata', 'system.json')
        call_command('loaddata', 'iso_metadata.json')
        call_command('loaddata', 'test_metadata.json')
