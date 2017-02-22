from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, modify_settings
from django.test.utils import setup_test_environment

from aristotle_mdr.contrib.links import models, perms
from aristotle_mdr.models import Workgroup, ObjectClass
from aristotle_mdr.tests import utils

from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages


setup_test_environment()


def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0, interactive=False)


class RelationViewPage(LoggedInViewConceptPages, TestCase):
    url_name = 'relation'
    itemType = models.Relation
    defaults = {'arity': 2}


class RelationAdminPage(AdminPageForConcept, TestCase):
    itemType = models.Relation
    create_defaults = {'arity': 2}
    form_defaults = {
        'arity': 2,
        'relationrole_set-TOTAL_FORMS':0,
        'relationrole_set-INITIAL_FORMS':0,
        'relationrole_set-MAX_NUM_FORMS':1,
    }


class LinkTestBase(utils.LoggedInViewPages):
    def setUp(self, *args, **kwargs):
        super(LinkTestBase, self).setUp(*args, **kwargs)
        self.item1 = ObjectClass.objects.create(
            name="Test Item 1 (visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg1,
        )
        self.item2 = ObjectClass.objects.create(
            name="Test Item 2 (NOT visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg2,
        )
        self.item3 = ObjectClass.objects.create(
            name="Test Item 3 (visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg1,
        )
        self.item4 = ObjectClass.objects.create(
            name="Test Item 4 (visible to only superusers)",
            definition="my definition",
        )
        
        self.relation = models.Relation.objects.create(name="test_relation", definition="Used for testing", arity=2)
        self.relation_role1 = models.RelationRole.objects.create(
            name="part1", definition="first role", multiplicity=1,
            ordinal=1,
            relation=self.relation
        )
        self.relation_role2 = models.RelationRole.objects.create(
            name="part2", definition="second role", multiplicity=1,
            ordinal=2,
            relation=self.relation
        )

        self.link1 = models.Link.objects.create(relation=self.relation)
        self.link1_end1 = self.link1.add_link_end(
            role = self.relation_role1,
            concept = self.item1
        )
        self.link1_end2 = self.link1.add_link_end(
            role = self.relation_role2,
            concept = self.item2
        )

        self.link2 = models.Link.objects.create(relation=self.relation)
        self.link2_end1 = self.link2.add_link_end(
            role = self.relation_role1,
            concept = self.item2
        )
        self.link2_end2 = self.link2.add_link_end(
            role = self.relation_role2,
            concept = self.item4
        )

class TestLinkPages(LinkTestBase, TestCase):
    def test_superuser_can_view_edit_links(self):
        self.login_superuser()
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.relation.name)
        self.assertContains(response, "Edit link")
        self.assertContains(response, reverse('aristotle_mdr_links:edit_link', args=[self.link1.pk]))

        response = self.client.get(self.item2.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.relation.name)
        self.assertContains(response, "Edit link")
        self.assertContains(response, reverse('aristotle_mdr_links:edit_link', args=[self.link2.pk]))

    def test_anon_user_cannot_view_edit_links(self):
        self.ra.register(
            item=self.item1,
            state=self.ra.public_state,
            user=self.su
        )
        self.logout()
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.relation.name)
        self.assertNotContains(response, "Edit link")
        self.assertNotContains(response, reverse('aristotle_mdr_links:edit_link', args=[self.link1.pk]))

    def test_editor_user_can_view_edit_links(self):
        self.login_editor()
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.relation.name)
        self.assertContains(response, "Edit link")
        self.assertContains(response, reverse('aristotle_mdr_links:edit_link', args=[self.link1.pk]))

        self.ra.register(
            item=self.item2,
            state=self.ra.public_state,
            user=self.su
        )
        response = self.client.get(self.item2.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.relation.name)
        self.assertFalse(perms.user_can_change_link(self.editor,self.link2))
        self.assertContains(response, reverse('aristotle_mdr_links:edit_link', args=[self.link1.pk]))
        self.assertNotContains(response, reverse('aristotle_mdr_links:edit_link', args=[self.link2.pk]))

    def test_editor_user_can_view_some_edit_link_pages(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle_mdr_links:edit_link', args=[self.link2.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('aristotle_mdr_links:edit_link', args=[self.link2.pk]),
            {
                "role_%s"%self.relation_role1.pk: [self.item1.pk],
                "role_%s"%self.relation_role2.pk: [self.item3.pk]
            }
        )
        self.assertTrue(self.item1 in self.link1.concepts())
        self.assertTrue(self.item3 not in self.link1.concepts())
        self.assertTrue(self.item2 in self.link1.concepts())
        self.assertEqual(response.status_code, 403)


        response = self.client.get(reverse('aristotle_mdr_links:edit_link', args=[self.link1.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle_mdr_links:edit_link', args=[self.link1.pk]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(
            reverse('aristotle_mdr_links:edit_link', args=[self.link1.pk]),
            {
                "role_%s"%self.relation_role1.pk: [self.item1.pk],
                "role_%s"%self.relation_role2.pk: [self.item3.pk]
            }
        )
        self.assertEqual(response.status_code, 302)  # Success!
        self.assertTrue(self.item1 in self.link1.concepts())
        self.assertTrue(self.item2 not in self.link1.concepts())
        self.assertTrue(self.item3 in self.link1.concepts())
        

class TestLinkPerms(LinkTestBase, TestCase):
    def test_superuser_can_edit_links(self):
        user = self.su
        self.assertTrue(perms.user_can_change_link(user,self.link1))
        self.assertTrue(perms.user_can_change_link(user,self.link2))

    def test_editor_can_edit_some_links(self):
        user = self.editor
        self.assertTrue(perms.user_can_change_link(user,self.link1))
        self.assertFalse(perms.user_can_change_link(user,self.link2))

    def test_viewer_can_edit_no_links(self):
        user = self.viewer
        self.assertFalse(perms.user_can_change_link(user,self.link1))
        self.assertFalse(perms.user_can_change_link(user,self.link2))

    def test_registrar_can_edit_no_links(self):
        user = self.registrar
        self.assertFalse(perms.user_can_change_link(user,self.link1))
        self.assertFalse(perms.user_can_change_link(user,self.link2))
