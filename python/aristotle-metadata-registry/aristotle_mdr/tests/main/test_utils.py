from django.test import TestCase

from aristotle_mdr import models

from aristotle_mdr.utils import setup_aristotle_test_environment

from aristotle_mdr import utils

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

import datetime

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

    def test_get_aristotle_url(self):

        user = get_user_model().objects.create(
            email='user@example.com',
            password='verysecure'
        )

        item = models.ObjectClass.objects.create(name="tname",definition="my definition",submitter=None)
        ra = models.RegistrationAuthority.objects.create(name="tname",definition="my definition")
        org = models.Organization.objects.create(name="tname",definition="my definition")
        wg = models.Workgroup.objects.create(name="tname",definition="my definition")
        rr = models.ReviewRequest.objects.create(
            requester=user,
            registration_authority=ra,
            state=ra.public_state,
            registration_date=datetime.date(2010,1,1)
        )

        url = utils.get_aristotle_url(item._meta.label_lower, item.pk, item.name)
        self.assertEqual(url, reverse('aristotle:item', args=[item.pk]))

        url = utils.get_aristotle_url(ra._meta.label_lower, ra.pk, ra.name)
        self.assertEqual(url, reverse('aristotle:registrationAuthority', args=[ra.pk, ra.name]))

        url = utils.get_aristotle_url(org._meta.label_lower, org.pk, org.name)
        self.assertEqual(url, reverse('aristotle:organization', args=[org.pk, org.name]))

        url = utils.get_aristotle_url(wg._meta.label_lower, wg.pk, wg.name)
        self.assertEqual(url, reverse('aristotle:workgroup', args=[wg.pk, wg.name]))

        url = utils.get_aristotle_url(rr._meta.label_lower, rr.pk)
        self.assertEqual(url, reverse('aristotle:userReviewDetails', args=[rr.pk]))

        url = utils.get_aristotle_url('aristotle_mdr.fake_model', 7, 'fake_name')
        self.assertTrue(url is None)
