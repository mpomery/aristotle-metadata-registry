from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment

from aristotle_mdr.contrib.slots import models
from aristotle_mdr.models import ObjectClass, Workgroup
from aristotle_mdr.tests import utils

setup_test_environment()


class TestSlotsPagesLoad(utils.LoggedInViewPages, TestCase):
    def test_similar_slots_page(self):
        _type = models.SlotDefinition.objects.create(
            slot_name="test slots",
            app_label='aristotle_mdr',
            concept_type='objectclass'
        )

        # Will be glad to not have so many cluttering workgroups everywhere!
        wg = Workgroup.objects.create(name='test wg')
        oc1 = ObjectClass.objects.create(
            name="test obj1",
            definition="test",
            workgroup=wg
        )
        oc2 = ObjectClass.objects.create(
            name="test  obj2",
            definition="test",
            workgroup=wg
        )
        models.Slot.objects.create(concept=oc1.concept, type=_type, value=1)
        models.Slot.objects.create(concept=oc2.concept, type=_type, value=2)

        self.login_superuser()
        # Test with no value
        response = self.client.get(reverse('aristotle_slots:similar_slots', args=[_type.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, oc1.name)
        self.assertContains(response, oc2.name)

        # Test with value is 1
        response = self.client.get(
            reverse('aristotle_slots:similar_slots', args=[_type.id]),
            {'value': 1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, oc1.name)
        self.assertNotContains(response, oc2.name)

        self.logout()
        # Test with no value
        response = self.client.get(reverse('aristotle_slots:similar_slots', args=[_type.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, oc1.name)
        self.assertNotContains(response, oc2.name)

    def test_long_slots(self):
        _type = models.SlotDefinition.objects.create(
            slot_name="test slots",
            app_label='aristotle_mdr',
            concept_type='objectclass'
        )

        oc1 = ObjectClass.objects.create(
            name="test obj1",
            definition="test",
        )

        slot = models.Slot.objects.create(concept=oc1.concept, type=_type, value="a" * 512)
        slot = models.Slot.objects.get(pk=slot.pk)
        self.assertTrue(slot.value=="a" * 512)
        self.assertTrue(len(slot.value) > 256)
