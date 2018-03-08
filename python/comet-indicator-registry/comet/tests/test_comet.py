from django.test import TestCase

import aristotle_mdr.models as MDR
from django.core.urlresolvers import reverse
from aristotle_mdr.tests.utils import ManagedObjectVisibility
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept

from aristotle_mdr.utils import setup_aristotle_test_environment
setup_aristotle_test_environment()

from comet import models

def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0, interactive=False)

class IndicatorVisibility(ManagedObjectVisibility,TestCase):
    def setUp(self):
        super(IndicatorVisibility, self).setUp()
        self.item = models.Indicator.objects.create(name="Test Indicator",
            workgroup=self.wg,
            )

class IndicatorAdmin(AdminPageForConcept,TestCase):
    itemType=models.Indicator

class IndicatorViewPage(LoggedInViewConceptPages,TestCase):
    url_name='indicator'
    itemType=models.Indicator
