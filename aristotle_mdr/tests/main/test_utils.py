from django.test import TestCase
from django.core.management import call_command
from django.urls import reverse

from aristotle_mdr import models
import datetime

from aristotle_mdr.utils import setup_aristotle_test_environment

from aristotle_mdr import utils

setup_aristotle_test_environment()


class UtilsTests(TestCase):
    def test_reverse_slugs(self):
        item = models.ObjectClass.objects.create(name=" ",definition="my definition",submitter=None)
        ra = models.RegistrationAuthority.objects.create(name=" ",definition="my definition")
        org = models.Organization.objects.create(name=" ",definition="my definition")
        wg = models.Workgroup.objects.create(name=" ",definition="my definition")

        self.assertTrue('--' in utils.url_slugify_concept(item))
        self.assertTrue('--' in utils.url_slugify_workgroup(wg))
        self.assertTrue('--' in utils.url_slugify_registration_authoritity(ra))
        self.assertTrue('--' in utils.url_slugify_organization(org))
