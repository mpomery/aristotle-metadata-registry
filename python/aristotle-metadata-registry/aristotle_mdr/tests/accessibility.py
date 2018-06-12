import sys
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse

import aristotle_mdr.models as models
import aristotle_mdr.tests.utils as utils
from wcag_zoo.validators import parade

import subprocess
import pprint

from aristotle_mdr.utils import setup_aristotle_test_environment

setup_aristotle_test_environment()

# This wont run on test aristotle_mdr.test because it is not prefixed with test_

MEDIA_TYPES = [
    [],
    #['(max-device-width: 480px)'],
    ['(max-width: 599px)'],
    ['(min-width: 600px)'],
    # ['(min-width: 992px)'],
    # ['(min-width: 1200px)'],
]

class TestWebPageAccessibilityBase(utils.LoggedInViewPages):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        self.wg = models.Workgroup.objects.create(name="Test WG 1")
        self.oc = models.ObjectClass.objects.create(name="Test OC 1")
        self.pr = models.Property.objects.create(name="Test Property 1")
        self.dec = models.DataElementConcept.objects.create(name="Test DEC 1", objectClass=self.oc, property=self.pr)
        self.vd = models.ValueDomain.objects.create(name="Test VD 1")
        self.cd = models.ConceptualDomain.objects.create(name="Test CD 1")
        self.de = models.DataElement.objects.create(name="Test DE 1", dataElementConcept=self.dec, valueDomain=self.vd)

        call_command('compilestatic', interactive=False, verbosity=0)
        call_command('collectstatic', interactive=False, verbosity=0)

        process = subprocess.Popen(
            ["ls", settings.STATIC_ROOT],
            stdout=subprocess.PIPE
        )
        dir_listing = process.communicate()[0].decode('utf-8')
        # Verify the static files are in the right place.
        assert('admin' in dir_listing)
        assert('aristotle_mdr' in dir_listing)
        assert('COMPILED' in dir_listing)
        print("All setup")

    def pages_tester(self, pages, media_types=MEDIA_TYPES):
        self.login_superuser()
        failures = 0
        total_results = []
        for url in pages:
            print()
            print("Testing url for WCAG compliance [%s] " % url, end="", flush=True, file=sys.stderr)
            print('*', end="", flush=True, file=sys.stderr)

            response = self.client.get(url, follow=True)
            self.assertTrue(response.status_code == 200)
            html = response.content

            for media in media_types:
                results = parade.Parade(
                    level='AA', staticpath=settings.BASE_STATICPATH,
                    skip_these_classes=['sr-only'],
                    ignore_hidden = True,
                    media_types = media
                ).validate_document(html)
                total_results.append(results)

                if len(results['failures']) != 0:  # NOQA - This shouldn't ever happen, so no coverage needed
                    pp = pprint.PrettyPrinter(indent=4)
                    pp.pprint("Failures for '%s' with media rules [%s]" % (url, media))
                    pp.pprint(results['failures'])
                    pp.pprint(results['warnings'])
                    print('Skipped')
                    pp.pprint(results['skipped'])
                    print("%s failures!!" % len(results['failures']) )
                    failures += len(results['failures'])
                else:
                    print('+', end="", flush=True, file=sys.stderr)

        for results in total_results:
            self.assertTrue(len(results['failures']) == 0)
        self.assertTrue(failures == 0)


class TestStaticPageAccessibility(TestWebPageAccessibilityBase, TestCase):
    def test_static_pages(self):
        from aristotle_mdr.urls.aristotle import urlpatterns
        pages = [
            reverse("aristotle:%s" % u.name) for u in urlpatterns
            if hasattr(u, 'name') and u.name is not None and u.regex.groups == 0
        ]


        self.pages_tester(pages)

class TestMetadataItemPageAccessibility(TestWebPageAccessibilityBase, TestCase):
    def test_metadata_object_pages(self):
        self.login_superuser()

        pages = [
            item.get_absolute_url() for item in [
                self.oc,
                self.pr,
                self.dec,
                self.vd,
                self.de,
                self.cd,
            ]
        ]
        self.pages_tester(pages)

class TestMetadataActionPageAccessibility(TestWebPageAccessibilityBase, TestCase):
    def test_metadata_object_action_pages(self):
        self.login_superuser()

        items = [
                self.oc,
                self.pr,
                self.dec,
                self.vd,
                self.de,
                self.cd,
        ]

        pages = [
            url
            for item in items
            for url in [
                reverse("aristotle:supersede", args=[item.id]),
                reverse("aristotle:deprecate", args=[item.id]),
                reverse("aristotle:edit_item", args=[item.id]),
                reverse("aristotle:clone_item", args=[item.id]),
                reverse("aristotle:item_history", args=[item.id]),
                reverse("aristotle:registrationHistory", args=[item.id]),
                reverse("aristotle:check_cascaded_states", args=[item.id]),
                # reverse("aristotle:item_history", args=[item.id]),
                # reverse("aristotle:item_history", args=[item.id]),
            ]
            if self.client.get(url, follow=True).status_code == 200
        ]
        # We skip those pages that don't exist (like object class 'child metadata' pages)

        self.pages_tester(pages, media_types = [[], ['(min-width: 600px)']])
