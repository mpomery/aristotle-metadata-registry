from __future__ import print_function
import os
import tempfile
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.urlresolvers import reverse

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.tests.utils as utils
from wcag_zoo.validators import parade

import subprocess

from django.test.utils import setup_test_environment
setup_test_environment()

TMP_STATICPATH = tempfile.mkdtemp(suffix='static')
STATICPATH = TMP_STATICPATH+'/static'
if not os.path.exists(STATICPATH):
    os.makedirs(STATICPATH)


class TestWebPageAccessibility(utils.LoggedInViewPages, TestCase):

    @override_settings(STATIC_ROOT = STATICPATH)
    def setUp(self):
        super(TestWebPageAccessibility, self).setUp()
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        self.wg = models.Workgroup.objects.create(name="Test WG 1")
        self.oc = models.ObjectClass.objects.create(name="Test OC 1")
        self.pr = models.Property.objects.create(name="Test Property 1")
        self.dec = models.DataElementConcept.objects.create(name="Test DEC 1", objectClass=self.oc, property=self.pr)
        self.vd = models.ValueDomain.objects.create(name="Test DE 1")
        self.de = models.DataElement.objects.create(name="Test VD 1", dataElementConcept=self.dec, valueDomain=self.vd)

        self.staticpath = TMP_STATICPATH
        call_command('collectstatic', interactive=False, verbosity=0)
        
        process = subprocess.Popen(
            ["ls", STATICPATH],
            stdout=subprocess.PIPE
        )
        dir_listing = process.communicate()[0]
        # Verify the static files are in the right place.
        self.assertTrue(b'admin' in dir_listing)
        self.assertTrue(b'aristotle_mdr' in dir_listing)
        print("All setup")

    def tearDown(self):
        
        # Maximum effort!
        process = subprocess.Popen(
            ["rm", self.staticpath, '-rf'],
            stdout=subprocess.PIPE
        )


    def pages_tester(self, pages):
        self.login_superuser()

        failures = 0
        for url in pages:
            response = self.client.get(url, follow=True)
            self.assertTrue(response.status_code == 200)
            html = response.content
    
            # if hasattr(html, 'decode'):  # Forgive me: Python 2 compatability
            #     html = html.decode('utf-8')
            
            results = parade.Parade(
                level='AA', staticpath=self.staticpath,
                skip_these_classes=['sr-only']
            ).validate_document(html)
            if len(results['failures']) != 0:  # NOQA - This shouldn't ever happen, so no coverage needed
                import pprint
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(url)
                pp.pprint(results['failures'])
                pp.pprint(results['warnings'])
                print("%s failures!!" % len(results['failures']) )
            else:
                print('+', end="")

        self.assertTrue(len(results['failures']) == 0)            

    def test_static_pages(self):
        from aristotle_mdr.urls.aristotle import urlpatterns
        pages = [
            reverse("aristotle:%s" % u.name) for u in urlpatterns
            if hasattr(u, 'name') and u.name is not None and u.regex.groups == 0
        ]

        self.pages_tester(pages)

    def test_object_pages(self):
        self.login_superuser()
        
        response = self.client.get(
            reverse('aristotle:item',args=[self.oc.id]),
            follow=True
        )
        self.assertTrue(response.status_code == 200)
        html = response.content

        if hasattr(html, 'decode'):  # Forgive me: Python 2 compatability
            html = html.decode('utf-8')
        
        results = parade.Parade(
            level='AA', staticpath=self.staticpath,
            ignore_these_classes=['sr-only']
        ).validate_document(html)
        if len(results['failures']) != 0:  # NOQA - This shouldn't ever happen, so no coverage needed
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(results['failures'])
            pp.pprint(results['warnings'])
            print("%s failures!!" % len(results['failures']) )
        self.assertTrue(len(results['failures']) == 0)
        