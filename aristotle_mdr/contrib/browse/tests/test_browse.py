from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment
from django.utils import timezone

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
from aristotle_mdr.utils import url_slugify_concept
from aristotle_mdr.forms.creation_wizards import WorkgroupVerificationMixin,CheckIfModifiedMixin

setup_test_environment()
from aristotle_mdr.tests import utils
import datetime


class LoggedInViewConceptBrowsePages(utils.LoggedInViewPages):
    defaults = {}
    
    def setUp(self):
        super(LoggedInViewConceptBrowsePages, self).setUp()

        self.item1 = self.itemType.objects.create(name="Test Item 1 (visible to tested viewers)",definition=" ",workgroup=self.wg1,**self.defaults)
        self.item2 = self.itemType.objects.create(name="Test Item 2 (NOT visible to tested viewers)",definition=" ",workgroup=self.wg2,**self.defaults)
        self.item3 = self.itemType.objects.create(name="Test Item 3 (visible to tested viewers)",definition=" ",workgroup=self.wg1,**self.defaults)
        self.item4 = self.itemType.objects.create(name="Test Item 3 (visible to tested viewers)",definition=" ",workgroup=self.wg1,**self.defaults)
        self.ra.register(self.item4,self.ra.public_state,self.su)

    def test_browse_pages_load(self):
        response = self.client.get(reverse('browse_apps'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('browse_models', args=['aristotle_mdr']))
        self.assertEqual(response.status_code, 200)

    def test_anon_can_view_browse(self):
        self.logout()
        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name])
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item4.name in response.content)
        self.assertTrue(self.item2.name not in response.content)

    def test_editor_can_view_browse(self):
        self.login_editor()
        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name])
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item4.name in response.content)
        self.assertTrue(self.item2.name not in response.content)

    def test_editor_can_view_browse_with_filters(self):
        self.login_editor()
        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'f':'name__icontains:3'}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name not in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name in response.content)
        self.assertTrue(self.item4.name in response.content)

        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'f':'a_fake_query_that_fails:3'}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name in response.content)
        self.assertTrue(self.item4.name in response.content)

        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'f':'another_fake_query_that_fails'}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name in response.content)
        self.assertTrue(self.item4.name in response.content)

    def test_editor_can_view_browse_with_slot_filters(self):
        from aristotle_mdr.contrib.slots.models import Slot, SlotDefinition
        _type = SlotDefinition.objects.create(
            slot_name="test",
            app_label='aristotle_mdr',
            concept_type=self.item1.__class__._meta.model_name
        )

        self.login_editor()
        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'sf':'%s:hello'%_type.slot_name}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name not in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name not in response.content)
        self.assertTrue(self.item4.name not in response.content)

        slot = Slot.objects.create(concept=self.item1.concept, type=_type, value="hello")

        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'sf':'%s:hello'%_type.slot_name}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name not in response.content)
        self.assertTrue(self.item4.name not in response.content)

        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'sf':['%s:hello'%_type.slot_name,'%s:bye'%_type.slot_name]}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name not in response.content)
        self.assertTrue(self.item4.name not in response.content)

        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'sf':'another_fake_query_that_fails'}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name in response.content)
        self.assertTrue(self.item4.name in response.content)

    def test_editor_can_view_browse_with_two_slot_filters(self):
        from aristotle_mdr.contrib.slots.models import Slot, SlotDefinition
        slot_type_1 = SlotDefinition.objects.create(
            slot_name="test1",
            app_label='aristotle_mdr',
            concept_type=self.item1.__class__._meta.model_name
        )
        slot_type_2 = SlotDefinition.objects.create(
            slot_name="test2",
            app_label='aristotle_mdr',
            concept_type=self.item1.__class__._meta.model_name
        )

        self.login_editor()
        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'sf':'%s:hello'%slot_type_1.slot_name}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name not in response.content)
        self.assertTrue(self.item3.name not in response.content)

        # Make some slots
        Slot.objects.create(concept=self.item1.concept, type=slot_type_1, value="hello")
        Slot.objects.create(concept=self.item1.concept, type=slot_type_2, value="other")

        Slot.objects.create(concept=self.item3.concept, type=slot_type_1, value="hello")

        self.login_editor()
        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'sf':'%s:hello'%slot_type_1.slot_name}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item3.name in response.content)

        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name]),
            {'sf': [
                '%s:hello'%slot_type_1.slot_name,
                '%s:other'%slot_type_2.slot_name,
            ]}
            )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.item1.name in response.content)
        self.assertTrue(self.item2.name not in response.content)
        self.assertTrue(self.item3.name not in response.content)
        self.assertTrue(self.item4.name not in response.content)


class ObjectClassViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='objectClass'
    itemType=models.ObjectClass
class PropertyViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='property'
    itemType=models.Property
class UnitOfMeasureViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='unitOfMeasure'
    itemType=models.UnitOfMeasure
class ValueDomainViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='valueDomain'
    itemType=models.ValueDomain

class ConceptualDomainViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='conceptualDomain'
    itemType=models.ConceptualDomain
class DataElementConceptViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='dataElementConcept'
    itemType=models.DataElementConcept
class DataElementViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='dataElement'
    itemType=models.DataElement
    
    def test_template_overriden(self):
        """
        see file tests/apps/extension_test/templates/aristotle_mdr_browse/aristotle_mdr/dataelement_list.html
        """
        check_text = "This is a customised browse list of data elements"
        response = self.client.get(
            reverse("browse_concepts",args=[self.itemType._meta.app_label,self.itemType._meta.model_name])
        )
        self.assertTrue(check_text in response.content)

class DataElementDerivationViewPage(LoggedInViewConceptBrowsePages,TestCase):
    url_name='dataelementderivation'
    itemType=models.DataElementDerivation
