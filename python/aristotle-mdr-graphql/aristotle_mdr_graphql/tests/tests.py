from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse
from aristotle_mdr.tests import utils
from aristotle_mdr import models as mdr_models
from aristotle_dse import models as dse_models
from comet import models as comet_models
from graphene.test import Client as QLClient

import json
import datetime

class BaseGraphqlTestCase(utils.LoggedInViewPages):

    def setUp(self):

        super().setUp()
        self.client = Client()

        self.apiurl = reverse('aristotle_graphql:graphql_api')

        self.dec = mdr_models.DataElementConcept.objects.create(
            name='Test Data Element Concept',
            definition='Test Defn',
            workgroup=self.wg1
        )

        self.vd = mdr_models.ValueDomain.objects.create(
            name='Test Value Domain',
            definition='Test Defn',
            workgroup=self.wg1
        )

        self.de = mdr_models.DataElement.objects.create(
            name='Test Data Element',
            definition='Test Defn',
            workgroup=self.wg1,
            dataElementConcept=self.dec,
            valueDomain=self.vd
        )

    def post_query(self, qstring, expected_code=200):
        postdata = {
            'query': qstring
        }

        jsondata = json.dumps(postdata)
        response = self.client.post(self.apiurl, jsondata, 'application/json')
        self.assertEqual(response.status_code, expected_code)
        response_json = json.loads(response.content)
        return response_json


class GraphqlFunctionalTests(BaseGraphqlTestCase, TestCase):

    def setUp(self):

        super().setUp()

        self.oc = mdr_models.ObjectClass.objects.create(
            name='Test Object Class',
            definition='Test Defn',
            workgroup=self.wg1
        )

    def test_query_all_metadata(self):

        self.login_editor()
        response_json = self.post_query('{ metadata { edges { node { name } } } }')
        edges = response_json['data']['metadata']['edges']
        self.assertEqual(len(edges), 4)

    def test_load_graphiql(self):

        self.login_editor()

        response = self.client.get(self.apiurl, HTTP_ACCEPT='text/html')
        self.assertRedirects(response, reverse('aristotle_graphql:graphql_explorer'))

        response = self.client.get(self.apiurl+"?noexplorer", HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('graphene/graphiql.html')


        response = self.client.get(reverse('aristotle_graphql:graphql_explorer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('aristotle_mdr_graphql/explorer.html')

    def test_query_by_uuid(self):

        self.login_editor()

        uuid = self.oc.uuid
        querytext = '{{ metadata (uuid: "{}") {{ edges {{ node {{ name }} }} }} }}'.format(uuid)
        json_response = self.post_query(querytext)
        edges = json_response['data']['metadata']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], self.oc.name)

# Disable icontains and iexact tests for now
#    def test_query_icontains(self):
#
#        self.login_editor()
#        response_json = self.post_query('{ metadata (name_Icontains: \"object\") { edges { node { name } } } }')
#        edges = response_json['data']['metadata']['edges']
#
#        self.assertEqual(len(edges), 1)
#        self.assertEqual(edges[0]['node']['name'], self.oc.name)
#
#    def test_query_iexact(self):
#
#        self.login_editor()
#        response_json = self.post_query('{ metadata (name_Iexact: \"test object class\") { edges { node { name } } } }')
#        edges = response_json['data']['metadata']['edges']
#
#        self.assertEqual(len(edges), 1)
#        self.assertEqual(edges[0]['node']['name'], self.oc.name)

    def test_dse_query(self):

        self.login_editor()
        dse_models.DataSetSpecification.objects.create(
            name='Test DSS',
            definition='Test Defn',
            workgroup=self.wg1
        )

        response_json = self.post_query('{ datasetSpecifications { edges { node { name } } } }')
        edges = response_json['data']['datasetSpecifications']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test DSS')

    def test_comet_query(self):

        self.login_editor()
        comet_models.Indicator.objects.create(
            name='Test Indicator Set',
            definition='Test Defn',
            workgroup=self.wg1
        )

        response_json = self.post_query('{ indicators { edges { node { name } } } }')
        edges = response_json['data']['indicators']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Indicator Set')

    def test_query_related_foreign_key(self):
        # Test a query on an items fk relation

        self.login_editor()
        json_response = self.post_query('{ dataElements { edges { node { name dataElementConcept { name } valueDomain { name } } } } }')
        edges = json_response['data']['dataElements']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Data Element')
        self.assertEqual(edges[0]['node']['dataElementConcept']['name'], 'Test Data Element Concept')
        self.assertEqual(edges[0]['node']['valueDomain']['name'], 'Test Value Domain')

    def test_query_related_set(self):
        # Test a query on an items related_set

        self.login_editor()
        json_response = self.post_query('{ valueDomains { edges { node { name dataelementSet { edges { node { name } } } } } } }')
        edges = json_response['data']['valueDomains']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Value Domain')
        self.assertEqual(len(edges[0]['node']['dataelementSet']['edges']), 1)
        self.assertEqual(edges[0]['node']['dataelementSet']['edges'][0]['node']['name'], 'Test Data Element')

    def test_query_related_m2m(self):
        # Test a query on an items many to many relation

        ded = mdr_models.DataElementDerivation.objects.create(
            submitter=self.editor,
            name="My Calculation"
        )

        ded.inputs.add(self.de)

        self.assertTrue(ded.can_view(self.editor))
        self.assertTrue(self.de.can_view(self.editor))

        self.login_editor()

        query = '{ dataElementDerivations { edges { node { name inputs { edges { node { name } } } } } } }'
        json_response = self.post_query(query)
        edges = json_response['data']['dataElementDerivations']['edges']
        self.assertEqual(len(edges), 1)

        concept_edges = edges[0]['node']['inputs']['edges']
        self.assertEqual(len(concept_edges), 1)

        item_names = [self.de.name]

        for item in concept_edges:
            self.assertTrue(item['node']['name'] in item_names)

        # Test accessing an item user doesnt have permission to view through a many to many relation
        self.de.workgroup = None
        self.de.save()
        self.de = self.de.__class__.objects.get(pk=self.de.pk)
        self.assertFalse(self.de.can_view(self.editor))

        json_response = self.post_query(query)
        edges = json_response['data']['dataElementDerivations']['edges']
        concept_edges = edges[0]['node']['inputs']['edges']
        self.assertEqual(len(concept_edges), 0)

    def test_query_table_inheritance(self):
        # Test a query of a table inheritance property (from metadata to dataelement)

        self.login_editor()

        json_response = self.post_query('{{ metadata (uuid: "{}") {{ edges {{ node {{ name dataelement {{ id valueDomain {{ name }} }} }} }} }} }}'.format(self.de.uuid))
        edges = json_response['data']['metadata']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], self.de.name)
        self.assertEqual(edges[0]['node']['dataelement']['valueDomain']['name'], self.de.valueDomain.name)

        json_response = self.post_query('{{ metadata (uuid: "{}") {{ edges {{ node {{ name dataelement {{ id }} }} }} }} }}'.format(self.dec.uuid))
        edges = json_response['data']['metadata']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], self.dec.name)
        self.assertEqual(edges[0]['node']['dataelement'], None)


class GraphqlPermissionsTests(BaseGraphqlTestCase, TestCase):

    def test_query_workgroup_items(self):
        # Test querying items in the users workgroup

        self.login_editor() # Editor is in wg1
        json_response = self.post_query('{ metadata { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['metadata']['edges']), 3)

        json_response = self.post_query('{ dataElements { edges { node { name dataElementConcept { name } valueDomain { name } } } } }')
        edges = json_response['data']['dataElements']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Data Element')
        self.assertEqual(edges[0]['node']['dataElementConcept']['name'], 'Test Data Element Concept')
        self.assertEqual(edges[0]['node']['valueDomain']['name'], 'Test Value Domain')

    def test_query_non_workgroup_items(self):
        # Test querying items not in the users workgroup
        self.login_regular_user()

        json_response = self.post_query('{ metadata { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['metadata']['edges']), 0)

        json_response = self.post_query('{ dataElements { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['dataElements']['edges']), 0)

        json_response = self.post_query('{ dataElementConcepts { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['dataElementConcepts']['edges']), 0)

        json_response = self.post_query('{ valueDomains { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['valueDomains']['edges']), 0)

    def test_anon_request_toplevel(self):
        # Test  querying from top level with anon user

        self.client.logout()

        self.vd._is_public = True
        self.vd.save()

        self.assertTrue(self.vd.can_view(self.editor))

        json_response = self.post_query('{ dataElements { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['dataElements']['edges']), 0)

        json_response = self.post_query('{ dataElementConcepts { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['dataElementConcepts']['edges']), 0)

        json_response = self.post_query('{ valueDomains { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['valueDomains']['edges']), 1)
        self.assertEqual(json_response['data']['valueDomains']['edges'][0]['node']['name'], 'Test Value Domain')

    def test_query_not_allowed_foreign_key(self):
        # Test accessing an item user doesnt have permission to view through a foreign key

        self.vd.workgroup = self.wg2
        self.vd.save()

        self.login_editor()
        self.assertFalse(self.vd.can_view(self.editor))

        json_response = self.post_query('{ dataElements { edges { node { name dataElementConcept { name } valueDomain { name } } } } }')
        edges = json_response['data']['dataElements']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Data Element')
        self.assertEqual(edges[0]['node']['dataElementConcept']['name'], 'Test Data Element Concept')
        self.assertEqual(edges[0]['node']['valueDomain'], None)

    def test_query_not_allowed_related_set(self):
        # Test accessing an item user doesnt have permission to view through a related set

        self.de.workgroup = self.wg2
        self.de.save()

        self.login_editor()

        json_response = self.post_query('{ valueDomains { edges { node { name dataelementSet { edges { node { name } } } } } } }')
        edges = json_response['data']['valueDomains']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Value Domain')
        self.assertEqual(len(edges[0]['node']['dataelementSet']['edges']), 0)

    # Filtering out RRs for now.
    # When we can perform actions against RRs, then we'll bring them back
    # def test_reviewrequest_query_perms(self):

    #     allowed_rr = mdr_models.ReviewRequest.objects.create(
    #         requester=self.editor,
    #         registration_authority=self.ra,
    #         status=0,
    #         state=1,
    #         registration_date=datetime.date.today(),
    #         cascade_registration=0
    #     )

    #     disallowed_rr = mdr_models.ReviewRequest.objects.create(
    #         requester=self.viewer,
    #         registration_authority=self.ra,
    #         status=0,
    #         state=0,
    #         registration_date=datetime.date.today(),
    #         cascade_registration=0
    #     )

    #     self.login_editor()

    #     json_response = self.post_query('{ reviewRequests { edges { node { id state } } } }')
    #     edges = json_response['data']['reviewRequests']['edges']

    #     self.assertEqual(len(edges), 1)
    #     self.assertEqual(edges[0]['node']['state'], 'A_1')

    def test_query_non_registered_item(self):
        # Test requesting an object without a defined node e.g. User

        json_response = self.post_query('{ metadata { submitter } }', 400)
        self.assertTrue('errors' in json_response.keys())
        self.assertFalse('data' in json_response.keys())
