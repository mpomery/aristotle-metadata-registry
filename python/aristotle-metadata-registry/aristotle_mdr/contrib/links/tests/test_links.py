from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import TestCase, tag

from aristotle_mdr.contrib.links import models, perms
from aristotle_mdr.models import ObjectClass, STATES
from aristotle_mdr.tests import utils
from aristotle_mdr.utils import setup_aristotle_test_environment, url_slugify_concept

from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.main.test_wizards import ConceptWizardPage

setup_aristotle_test_environment()


def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0, interactive=False)


class RelationViewPage(LoggedInViewConceptPages, TestCase):
    url_name = 'relation'
    itemType = models.Relation
    defaults = {'arity': 2}

    def setUp(self):
        super().setUp()

        for i in range(4):
            models.RelationRole.objects.create(
                name="test name",
                definition="test definition",
                relation=self.item1,
                ordinal=i,
                multiplicity=3,
            )

    def test_weak_editing_in_advanced_editor_dynamic(self):
        super().test_weak_editing_in_advanced_editor_dynamic(updating_field='definition')


class RelationAdminPage(AdminPageForConcept, TestCase):
    itemType = models.Relation
    create_defaults = {'arity': 2}
    form_defaults = {
        'arity': 2,
        'relationrole_set-TOTAL_FORMS':0,
        'relationrole_set-INITIAL_FORMS':0,
        'relationrole_set-MAX_NUM_FORMS':1,
    }


class RelationCreationWizard(utils.FormsetTestUtils, ConceptWizardPage, TestCase):
    model=models.Relation
    extra_step2_data = {'results-arity': 2}

    @tag('edit_formsets')
    def test_weak_editor_during_create(self):

        self.login_editor()

        item_name = 'My New Relation'
        step_1_data = {
            self.wizard_form_name+'-current_step': 'initial',
            'initial-name': item_name,
        }

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, 'results')

        step_2_data = {
            self.wizard_form_name+'-current_step': 'results',
            'initial-name':item_name,
            'results-name':item_name,
            'results-definition':"Test Definition",
            'results-arity': 2
        }

        role_formset_data = [
            {'name': 'parent', 'definition': 'ok', 'multiplicity': 1, 'ORDER': 0},
            {'name': 'child', 'definition': 'good', 'multiplicity': 1, 'ORDER': 1}
        ]

        step_2_data.update(self.get_formset_postdata(role_formset_data, 'roles'))

        response = self.client.post(self.wizard_url, step_2_data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.model.objects.filter(name=item_name).exists())
        self.assertEqual(self.model.objects.filter(name=item_name).count(),1)
        item = self.model.objects.filter(name=item_name).first()
        self.assertRedirects(response,url_slugify_concept(item))

        roles = item.relationrole_set.all().order_by('ordinal')

        self.assertEqual(roles[0].ordinal, 0)
        self.assertEqual(roles[0].name, 'parent')
        self.assertEqual(roles[0].definition, 'ok')
        self.assertEqual(roles[0].multiplicity, 1)

        self.assertEqual(roles[1].ordinal, 1)
        self.assertEqual(roles[1].name, 'child')
        self.assertEqual(roles[1].definition, 'good')
        self.assertEqual(roles[1].multiplicity, 1)


class LinkTestBase(utils.LoggedInViewPages):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
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

    def test_add_link_wizard(self):
        self.wizard_form_name = "add_link_wizard"
        next_url = reverse("aristotle:home")
        self.wizard_url = reverse('aristotle_mdr_links:add_link')+'?next=' + next_url

        self.ra.register(
            item=self.relation,
            state=STATES.standard,
            user=self.su
        )
        self.item1.linkend_set.all().delete()

        self.assertTrue(self.relation.can_view(self.editor))
        self.assertEqual(self.item1.linkend_set.count(), 0)
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login

        self.login_editor()

        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)  # OK, lets go!
        self.assertContains(response, "add_link_wizard-current_step")

        step_0_data = {
            self.wizard_form_name+'-current_step': '0',
        }

        response = self.client.post(self.wizard_url, step_0_data)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, '0')
        self.assertTrue('relation' in wizard['form'].errors.keys())

        # must submit a relation
        step_0_data.update({'0-relation': str(self.relation.pk)})
        # success!

        response = self.client.post(self.wizard_url, step_0_data)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)  # OK, lets go!

        self.assertEqual(wizard['steps'].current, '1')
        self.assertFalse('relation' in wizard['form'].errors.keys())

        self.assertEqual(response.status_code, 200)

        step_1_data = {}
        step_1_data.update(step_0_data)
        step_1_data.update({self.wizard_form_name+'-current_step': '1'})
        for role in self.relation.relationrole_set.all():
            step_1_data.update({'1-role_%s'%role.pk: self.item1.pk})

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)  # OK, lets go!

        self.assertEqual(len(wizard['form'].errors.keys()), 0)
        self.assertEqual(wizard['steps'].current, '2')

        step_2_data = {}
        step_2_data.update(step_1_data)
        step_2_data.update({self.wizard_form_name+'-current_step': '2'})
        response = self.client.post(self.wizard_url, step_2_data)
        self.assertRedirects(response, next_url)

        self.assertEqual(self.item1.linkend_set.count(), self.relation.relationrole_set.count())


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

    def test_who_can_make_links(self):
        # Anyone who has an active account is an editor, so everyone can make links
        self.assertTrue(perms.user_can_make_link(self.registrar))
        self.assertTrue(perms.user_can_make_link(self.viewer))
        self.assertTrue(perms.user_can_make_link(self.editor))
        self.assertTrue(perms.user_can_make_link(self.su))

    def test_cannot_save_linkend_with_bad_role(self):
        self.new_relation = models.Relation.objects.create(
            name="another_test_relation", definition="Used for testing",
        )

        self.new_link = models.Link.objects.create(relation=self.new_relation)
        self.assertNotEqual(self.new_link.relation, self.relation_role1.relation)

        with self.assertRaises(ValidationError):
            self.link_end_bad = self.new_link.add_link_end(
                role = self.relation_role1,
                concept = self.item1
            )


class TestLinkAssortedPages(LinkTestBase, TestCase):
    def test_link_json_page(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle_mdr_links:link_json_for_item', args=[self.item1.pk]))
        self.assertEqual(response.status_code,200)
