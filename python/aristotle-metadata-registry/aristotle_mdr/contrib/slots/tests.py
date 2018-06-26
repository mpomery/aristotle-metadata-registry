from django.urls import reverse
from django.test import TestCase, tag

from aristotle_mdr.contrib.slots import models
from aristotle_mdr import models as mdr_models
from aristotle_mdr.models import ObjectClass, Workgroup
from aristotle_mdr.tests import utils
from aristotle_mdr.tests.main.test_bulk_actions import BulkActionsTest
from aristotle_mdr.utils import setup_aristotle_test_environment
from aristotle_mdr.contrib.slots.utils import concepts_with_similar_slots

import datetime
import json

setup_aristotle_test_environment()


class BaseSlotsTestCase(utils.LoggedInViewPages):

    def setUp(self):
        super().setUp()

        self.newoc = ObjectClass.objects.create(
            name='testoc',
            definition='test defn',
            workgroup=self.wg1,
            submitter=self.editor
        )

        public_slot = models.Slot.objects.create(
            name='public',
            type='string',
            value='test value',
            concept=self.newoc,
            order=0,
            permission=0
        )
        auth_slot = models.Slot.objects.create(
            name='auth',
            type='string',
            value='test value',
            concept=self.newoc,
            order=1,
            permission=1
        )
        work_slot = models.Slot.objects.create(
            name='work',
            type='string',
            value='test value',
            concept=self.newoc,
            order=2,
            permission=2
        )

    # ------- utils ------

    def get_aristotle_item(self, id):
        response = self.client.get(reverse('aristotle:item', args=[id]), follow=True)
        self.assertEqual(response.status_code, 200)
        return response

    def get_aristotle_edit(self, id, code=200):
        response = self.client.get(reverse('aristotle:edit_item', args=[id]))
        self.assertEqual(response.status_code, code)
        return response

    def make_newoc_public(self):
        review = mdr_models.ReviewRequest.objects.create(
            requester=self.su,
            registration_authority=self.ra,
            state=self.ra.public_state,
            registration_date=datetime.date(2010, 1, 1)
        )
        review.concepts.add(self.newoc)
        self.ra.register(self.newoc, self.ra.public_state, self.registrar)


class SlotsPermissionTests(BaseSlotsTestCase, TestCase):

    def test_item_page_permissions(self):

        self.make_newoc_public()

        self.assertEqual(self.newoc.slots.count(), 3)
        self.assertTrue(self.newoc._is_public)

        # Anon User
        self.client.logout()
        response = self.get_aristotle_item(self.newoc.id)
        slots = response.context['slots']
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].name, 'public')

        # Authenticated User, Not in workgroup
        self.client.logout()
        self.login_regular_user()
        response = self.get_aristotle_item(self.newoc.id)
        slots = response.context['slots']
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0].name, 'public')
        self.assertEqual(slots[1].name, 'auth')

        # Authenticated user in workgroup
        self.client.logout()
        self.login_editor()
        response = self.get_aristotle_item(self.newoc.id)
        slots = response.context['slots']
        self.assertEqual(len(slots), 3)
        self.assertEqual(slots[0].name, 'public')
        self.assertEqual(slots[1].name, 'auth')
        self.assertEqual(slots[2].name, 'work')

    def test_edit_page_permissions(self):

        self.assertEqual(self.newoc.slots.count(), 3)

        # Anon user
        self.client.logout()
        response = self.get_aristotle_edit(self.newoc.id, 302)
        # Should not be able to view edit page at all
        self.assertRedirects(
            response,
            reverse('friendly_login') + '?next=/item/' + str(self.newoc.id) + '/edit'
        )

        # Authenticated user, not in wg
        self.client.logout()
        self.login_regular_user()
        # Cant edit the item not in wg
        response = self.get_aristotle_edit(self.newoc.id, 403)

        # Authenticated user, editor in wg
        self.client.logout()
        self.login_editor()
        response = self.get_aristotle_edit(self.newoc.id)
        queryset = response.context['slots_FormSet'].queryset
        self.assertEqual(queryset[0].name, 'public')
        self.assertEqual(queryset[1].name, 'auth')
        self.assertEqual(queryset[2].name, 'work')

    def test_similar_slots_permissions(self):

        self.make_newoc_public()

        # Similar slots search should only display public slots
        self.assertEqual(self.newoc.slots.count(), 3)

        response = self.client.get(reverse('aristotle_slots:similar_slots', kwargs={'slot_name': 'public'}))
        self.assertContains(response, 'test value')
        self.assertEqual(len(response.context['object_list']), 1)

        response = self.client.get(reverse('aristotle_slots:similar_slots', kwargs={'slot_name': 'auth'}))
        self.assertContains(response, 'No metadata items have this slot type')
        self.assertEqual(len(response.context['object_list']), 0)

        response = self.client.get(reverse('aristotle_slots:similar_slots', kwargs={'slot_name': 'work'}))
        self.assertContains(response, 'No metadata items have this slot type')
        self.assertEqual(len(response.context['object_list']), 0)


class TestSlotsPagesLoad(utils.LoggedInViewPages, TestCase):
    def test_similar_slots_page(self):
        # from django.conf import settings
        # from django.utils.module_loading import import_string
        # conf = import_string(settings.ROOT_URLCONF)

        slot_name = 'my_slot_name'
        slot_type = ''

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
        models.Slot.objects.create(concept=oc1.concept, name=slot_name, type=slot_type, value=1)
        models.Slot.objects.create(concept=oc2.concept, name=slot_name, type=slot_type, value=2)

        self.login_superuser()
        # Test with no value
        response = self.client.get(reverse('aristotle_slots:similar_slots', kwargs={'slot_name': slot_name}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, oc1.name)
        self.assertContains(response, oc2.name)

        # Test with value is 1
        response = self.client.get(
            reverse('aristotle_slots:similar_slots', kwargs={'slot_name': slot_name}),
            {'value': 1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, oc1.name)
        self.assertNotContains(response, oc2.name)

        self.logout()
        # Test with no value
        response = self.client.get(reverse('aristotle_slots:similar_slots', kwargs={'slot_name': slot_name}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, oc1.name)
        self.assertNotContains(response, oc2.name)

    def test_long_slots(self):
        oc1 = ObjectClass.objects.create(
            name="test obj1",
            definition="test",
        )

        slot = models.Slot.objects.create(concept=oc1.concept, name="long slot", value="a" * 512)
        slot = models.Slot.objects.get(pk=slot.pk)
        self.assertTrue(slot.value=="a" * 512)
        self.assertTrue(len(slot.value) > 256)


class TestSlotsBulkAction(BulkActionsTest, TestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.item5 = ObjectClass.objects.create(name="OC5", definition="OC5 definition", workgroup=self.wg2)
        self.slot_name = 'my_name'
        self.slot_type = 'bulk_insert'

    def test_bulk_set_slot_on_permitted_items(self):
        self.login_editor()

        self.assertEqual(self.editor.profile.favourites.count(), 0)
        test_value = 'Insert Tab A into Slot B'
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.contrib.slots.forms.BulkAssignSlotsForm',
                'items': [self.item1.id, self.item2.id],
                'slot_name': self.slot_name,
                'slot_type': self.slot_type,
                'value': test_value,
                "confirmed": True
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(2, len(concepts_with_similar_slots(user=self.editor, name=self.slot_name, value=test_value)))
        self.assertEqual(2, len(concepts_with_similar_slots(user=self.editor, _type=self.slot_type, value=test_value)))

    def test_bulk_set_slot_on_forbidden_items(self):
        self.login_editor()

        self.assertEqual(self.editor.profile.favourites.count(), 0)
        test_value = 'Insert Tab A into Slot B'
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.contrib.slots.forms.BulkAssignSlotsForm',
                'items': [self.item1.id, self.item4.id, self.item5.id],
                'slot_name': self.slot_name,
                'slot_type': self.slot_type,
                'value': test_value,
                "confirmed": True
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, len(concepts_with_similar_slots(user=self.editor, name=self.slot_name, value=test_value)))
        self.assertEqual(1, len(concepts_with_similar_slots(user=self.editor, _type=self.slot_type, value=test_value)))
