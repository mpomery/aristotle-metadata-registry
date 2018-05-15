from django.test import TestCase, tag

import aristotle_mdr.models as MDR
from django.core.urlresolvers import reverse
from aristotle_mdr.tests.utils import ManagedObjectVisibility, FormsetTestUtils
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept
from aristotle_mdr.tests.main.test_wizards import ConceptWizardPage

from aristotle_mdr.utils import setup_aristotle_test_environment, url_slugify_concept
setup_aristotle_test_environment()

from aristotle_dse import models

def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0, interactive=False)

class DataSetSpecificationVisibility(ManagedObjectVisibility,TestCase):
    def setUp(self):
        super(DataSetSpecificationVisibility, self).setUp()
        self.item = models.DataSetSpecification.objects.create(name="Test DSS",
            workgroup=self.wg,
            )

class DataSetSpecificationAdmin(AdminPageForConcept,TestCase):
    itemType=models.DataSetSpecification
    form_defaults={
        'dssdeinclusion_set-TOTAL_FORMS':0,
        'dssdeinclusion_set-INITIAL_FORMS':0,
        'dsscdeinclusion_set-MAX_NUM_FORMS':1,
        'dssclusterinclusion_set-TOTAL_FORMS':0,
        'dssclusterinclusion_set-INITIAL_FORMS':0,
        'dssclusterinclusion_set-MAX_NUM_FORMS':1,
        }

class DataSetSpecificationViewPage(LoggedInViewConceptPages,TestCase):
    url_name='datasetspecification'
    itemType=models.DataSetSpecification

    def test_weak_editing_in_advanced_editor_dynamic(self):

        pass
        # Weak editing currently disabled on this model

        # oc = MDR.ObjectClass.objects.create(
        #     name="a very nice object class"
        # )
        # oc.save()
        #
        # de = MDR.DataElement.objects.create(
        #     name="test name",
        #     definition="test definition",
        # )
        # de.save()
        #
        # for i in range(4):
        #     models.DSSDEInclusion.objects.create(
        #         data_element=de,
        #         specific_information="test info",
        #         conditional_obligation="test obligation",
        #         order=i,
        #         dss=self.item1
        #     )
        # for i in range(4):
        #     inc = models.DSSDEInclusion.objects.create(
        #         data_element=de,
        #         specific_information="test info",
        #         conditional_obligation="test obligation",
        #         order=i,
        #         dss=self.item1
        #     )
        #     clust = models.DSSClusterInclusion.objects.create(
        #         specific_information="test info",
        #         conditional_obligation="test obligation",
        #         order=i,
        #         dss=self.item1,
        #         child=self.item1
        #     )
        #
        #
        # #self.item1.addCluster(child=self.item3)
        # default_fields = {
        #     'specialisation_classes': oc.id,
        #     'data_element': de.id,
        #     'child': self.item1.id
        # }
        #
        # super().test_weak_editing_in_advanced_editor_dynamic(updating_field='specific_information', default_fields=default_fields)

    def test_add_data_element(self):
        de,created = MDR.DataElement.objects.get_or_create(name="Person-sex, Code N",
            workgroup=self.wg1,definition="The sex of the person with a code.",
            )
        self.item1.addDataElement(de)
        self.assertTrue(self.item1.data_elements.count(),1)

    def test_cascade_action(self):
        self.logout()
        check_url = reverse('aristotle:check_cascaded_states', args=[self.item1.pk])
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,302)
        # self.assertNotContains(response, check_url)  # No content on the page as the user was redirected to a login page

        response = self.client.get(check_url)
        self.assertTrue(response.status_code,403)

        self.login_editor()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response, check_url)  # no child items, nothing to review

        response = self.client.get(check_url)
        self.assertTrue(response.status_code,403)

        self.test_add_data_element()  # add a data element

        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, check_url)  # now there are child items, we can review

        response = self.client.get(check_url)
        self.assertTrue(response.status_code,200)


class DataCatalogViewPage(LoggedInViewConceptPages,TestCase):
    url_name='datacatalog'
    itemType=models.DataCatalog


class DatasetViewPage(LoggedInViewConceptPages,TestCase):
    url_name='dataset'
    itemType=models.Dataset


class DistributionViewPage(LoggedInViewConceptPages,TestCase):
    url_name='distribution'
    itemType=models.Distribution

    def test_weak_editing_in_advanced_editor_dynamic(self):
        de = MDR.DataElement.objects.create(
            name="test name",
            definition="test definition",
        )
        oc = MDR.ObjectClass.objects.create(
            name="a very nice object class"
        )
        oc.save()

        for i in range(4):
            models.DistributionDataElementPath.objects.create(
                data_element=de,
                logical_path=str(i),
                order=i,
                distribution=self.item1,
            )

        default_fields = {
            'specialisation_classes': oc.id,
            'data_element': de.id
        }

        super().test_weak_editing_in_advanced_editor_dynamic(updating_field='logical_path', default_fields=default_fields)


class DistributionWizardPage(FormsetTestUtils, ConceptWizardPage, TestCase):
    model=models.Distribution

    def do_test_for_issue333(self,response):
        self.assertTrue(self.extra_wg in response.context['form'].fields['workgroup'].queryset)

    @tag('edit_formsets')
    def test_weak_editor_during_create(self):
        self.de1 = MDR.DataElement.objects.create(name='DE1 - visible',definition="my definition",workgroup=self.wg1)
        self.de2 = MDR.DataElement.objects.create(name='DE2 - visible',definition="my definition",workgroup=self.wg1)
        self.de3 = MDR.DataElement.objects.create(name='DE3 - visible',definition="my definition",workgroup=self.wg1)

        self.oc1 = MDR.ObjectClass.objects.create(name='OC1 - visible',definition="my definition",workgroup=self.wg1)
        self.oc2 = MDR.ObjectClass.objects.create(name='OC2 - visible',definition="my definition",workgroup=self.wg1)
        self.oc3 = MDR.ObjectClass.objects.create(name='OC3 - visible',definition="my definition",workgroup=self.wg1)

        self.login_editor()

        item_name = 'My Fancy New Distribution'
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
        }

        ddep_formset_data = [
            {'data_element': self.de1.pk, 'logical_path': '/garbage/file', 'specialisation_classes': [self.oc1.pk, self.oc3.pk], 'ORDER': 0},
            {'data_element': self.de3.pk, 'logical_path': '/garbage/file', 'specialisation_classes': [self.oc2.pk, self.oc3.pk], 'ORDER': 1},
        ]
        step_2_data.update(self.get_formset_postdata(ddep_formset_data, 'data_elements'))

        response = self.client.post(self.wizard_url, step_2_data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.model.objects.filter(name=item_name).exists())
        self.assertEqual(self.model.objects.filter(name=item_name).count(),1)
        item = self.model.objects.filter(name=item_name).first()
        self.assertRedirects(response,url_slugify_concept(item))

        ddeps = item.distributiondataelementpath_set.all().order_by('order')

        self.assertEqual(ddeps[0].order, 0)
        self.assertEqual(ddeps[0].data_element, self.de1)
        self.assertEqual(ddeps[0].logical_path, '/garbage/file')
        self.assertEqual(ddeps[0].specialisation_classes.count(), 2)
        self.assertTrue(self.oc1 in ddeps[0].specialisation_classes.all())
        self.assertTrue(self.oc3 in ddeps[0].specialisation_classes.all())

        self.assertEqual(ddeps[1].order, 1)
        self.assertEqual(ddeps[1].data_element, self.de3)
        self.assertEqual(ddeps[1].logical_path, '/garbage/file')
        self.assertEqual(ddeps[1].specialisation_classes.count(), 2)
        self.assertTrue(self.oc2 in ddeps[1].specialisation_classes.all())
        self.assertTrue(self.oc3 in ddeps[1].specialisation_classes.all())
