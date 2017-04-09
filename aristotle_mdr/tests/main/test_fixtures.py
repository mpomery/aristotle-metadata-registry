from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment

from django.core.management import call_command
from aristotle_mdr.contrib.help import models

try:
    setup_test_environment()
except RuntimeError as err:
    if "setup_test_environment() was already called" in err.msg:
        # The environment is setup, its all good.
        pass
    else:
        raise


class TestFixtures(TestCase):
    def test_fixtures(self):
        call_command('loaddata', 'system.json')
        call_command('loaddata', 'iso_metadata.json')
        call_command('loaddata', 'test_metadata.json')
