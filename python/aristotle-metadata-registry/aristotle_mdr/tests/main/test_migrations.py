from aristotle_mdr.tests.migrations import MigrationsTestCase
from django.core.exceptions import FieldDoesNotExist
from django.conf import settings
from django.test import TestCase

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
