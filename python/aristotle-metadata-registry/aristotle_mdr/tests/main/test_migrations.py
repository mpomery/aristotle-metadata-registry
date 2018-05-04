from aristotle_mdr.tests.migrations import MigrationsTestCase
from django.core.exceptions import FieldDoesNotExist
from django.conf import settings
from django.test import TestCase, tag

class TestSynonymMigration(MigrationsTestCase, TestCase):

    migrate_from = '0023_auto_20180206_0332'
    migrate_to = '0024_synonym_data_migration'

    def setUpBeforeMigration(self, apps):
        objectclass = apps.get_model('aristotle_mdr', 'ObjectClass')

        self.oc1 = objectclass.objects.create(
            name='Test OC',
            definition='Test Definition',
            synonyms='great'
        )

        self.oc2 = objectclass.objects.create(
            name='Test Blank OC',
            definition='Test Definition'
        )

    def test_migration(self):

        slot = self.apps.get_model('aristotle_mdr_slots', 'Slot')

        self.assertEqual(slot.objects.count(), 1)

        syn_slot = slot.objects.get(name='Synonyms')
        self.assertEqual(syn_slot.concept.name, self.oc1.name)
        self.assertEqual(syn_slot.concept.definition, self.oc1.definition)
        self.assertEqual(syn_slot.value, 'great')

class TestSynonymMigrationReverse(MigrationsTestCase, TestCase):

    migrate_from = '0024_synonym_data_migration'
    migrate_to = '0023_auto_20180206_0332'

    def setUpBeforeMigration(self, apps):
        objectclass = apps.get_model('aristotle_mdr', 'ObjectClass')
        slot = apps.get_model('aristotle_mdr_slots', 'Slot')

        self.oc = objectclass.objects.create(
            name='Test OC',
            definition='Test Definition',
            synonyms='great'
        )

        self.slot = slot.objects.create(
            name='Synonyms',
            concept=self.oc,
            value='amazing'
        )

    def test_migration(self):

        objectclass = self.apps.get_model('aristotle_mdr', 'ObjectClass')

        oc = objectclass.objects.get(pk=self.oc.pk)
        self.assertEqual(oc.synonyms, 'amazing')

class TestDedMigration(MigrationsTestCase, TestCase):

    migrate_from = '0026_auto_20180411_2323'
    #migrate_to = '0028_replace_old_ded_through'
    migrate_to = '0027_add_ded_through_models'

    def setUpBeforeMigration(self, apps):

        ded = apps.get_model('aristotle_mdr', 'DataElementDerivation')
        de = apps.get_model('aristotle_mdr', 'DataElement')

        self.ded1 = ded.objects.create(
            name='DED1',
            definition='test defn',
        )

        self.de1 = de.objects.create(
            name='DE1',
            definition='test defn',
        )

        self.de2 = de.objects.create(
            name='DE2',
            definition='test defn',
        )

        self.de3 = de.objects.create(
            name='DE3',
            definition='test defn',
        )

        self.ded1.derives.add(self.de1)
        self.ded1.derives.add(self.de2)
        self.ded1.inputs.add(self.de3)

    def test_migration(self):

        ded = self.apps.get_model('aristotle_mdr', 'DataElementDerivation')
        ded_inputs_through = self.apps.get_model('aristotle_mdr', 'DedInputsThrough')
        ded_derives_through = self.apps.get_model('aristotle_mdr', 'DedDerivesThrough')

        ded_obj = ded.objects.get(pk=self.ded1.pk)

        # Test through objects order

        items = ded_inputs_through.objects.filter(data_element_derivation=ded_obj)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.order, 0)
        self.assertEqual(item.data_element.pk, self.de3.pk)

        items = ded_derives_through.objects.filter(data_element_derivation=ded_obj).order_by('order')
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].order, 0)
        self.assertEqual(items[1].order, 1)

        de_pks = [item.data_element.pk for item in items]
        orig_de_pks = [self.de1.pk, self.de2.pk]

        self.assertEqual(set(de_pks), set(orig_de_pks))

class TestDedMigrationReverse(MigrationsTestCase, TestCase):

    migrate_from = '0027_add_ded_through_models'
    migrate_to = '0026_auto_20180411_2323'

    def setUpBeforeMigration(self, apps):

        ded = apps.get_model('aristotle_mdr', 'DataElementDerivation')
        de = apps.get_model('aristotle_mdr', 'DataElement')
        ded_inputs_through = apps.get_model('aristotle_mdr', 'DedInputsThrough')
        ded_derives_through = apps.get_model('aristotle_mdr', 'DedDerivesThrough')

        self.ded1 = ded.objects.create(
            name='DED1',
            definition='test defn',
        )

        self.de1 = de.objects.create(
            name='DE1',
            definition='test defn',
        )

        self.de2 = de.objects.create(
            name='DE2',
            definition='test defn',
        )

        self.de3 = de.objects.create(
            name='DE3',
            definition='test defn',
        )

        ded_derives_through.objects.create(
            data_element_derivation=self.ded1,
            data_element=self.de1,
            order=0
        )

        ded_derives_through.objects.create(
            data_element_derivation=self.ded1,
            data_element=self.de2,
            order=1
        )

        ded_inputs_through.objects.create(
            data_element_derivation=self.ded1,
            data_element=self.de3,
            order=0
        )

    def test_migration(self):

        ded = self.apps.get_model('aristotle_mdr', 'DataElementDerivation')
        ded_obj = ded.objects.get(pk=self.ded1.pk)

        derives_objs = ded_obj.derives.all()
        self.assertEqual(len(derives_objs), 2)
        self.assertTrue(self.de1 in derives_objs)
        self.assertTrue(self.de2 in derives_objs)

        inputs_objs = ded_obj.inputs.all()
        self.assertEqual(len(inputs_objs), 1)
        self.assertTrue(self.de3 in inputs_objs)
