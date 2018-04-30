from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse
from aristotle_mdr.tests import utils
from aristotle_mdr import models as mdr_models
from aristotle_dse import models as dse_models
from comet import models as comet_models

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
        self.assertEqual(response_json['data']['metadata']['edges'][0]['node']['name'], 'Test Object Class')

    def test_load_graphiql(self):

        self.login_editor()

        response = self.client.get(self.apiurl, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('graphene/graphiql.html')

    def test_query_by_uuid(self):

        self.login_editor()

        uuid = self.oc.uuid
        querytext = '{{ metadata (uuid: "{}") {{ edges {{ node {{ name }} }} }} }}'.format(uuid)
        json_response = self.post_query(querytext)
        edges = json_response['data']['metadata']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], self.oc.name)

    def test_query_icontains(self):

        self.login_editor()
        response_json = self.post_query('{ metadata (name_Icontains: \"test\") { edges { node { name } } } }')
        edges = response_json['data']['metadata']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], self.oc.name)

    def test_query_iexact(self):

        self.login_editor()
        response_json = self.post_query('{ metadata (name_Iexact: \"test object class\") { edges { node { name } } } }')
        edges = response_json['data']['metadata']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], self.oc.name)

    def test_dse_query(self):

        self.login_editor()
        dse_models.Dataset.objects.create(
            name='Test Dataset',
            definition='Test Defn',
            workgroup=self.wg1
        )

        response_json = self.post_query('{ datasets { edges { node { name } } } }')
        edges = response_json['data']['datasets']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Dataset')

    def test_comet_query(self):

        self.login_editor()
        comet_models.IndicatorSet.objects.create(
            name='Test Indicator Set',
            definition='Test Defn',
            workgroup=self.wg1
        )

        response_json = self.post_query('{ indicatorSets { edges { node { name } } } }')
        edges = response_json['data']['indicatorSets']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Indicator Set')

    def test_query_related_foreign_key(self):

        self.login_editor()
        json_response = self.post_query('{ dataElements { edges { node { name dataElementConcept { name } valueDomain { name } } } } }')
        edges = json_response['data']['dataElements']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Data Element')
        self.assertEqual(edges[0]['node']['dataElementConcept']['name'], 'Test Data Element Concept')
        self.assertEqual(edges[0]['node']['valueDomain']['name'], 'Test Value Domain')

    def test_query_related_set(self):

        self.login_editor()
        json_response = self.post_query('{ valueDomains { edges { node { name dataelementSet { edges { node { name } } } } } } }')
        edges = json_response['data']['valueDomains']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Value Domain')
        self.assertEqual(len(edges[0]['node']['dataelementSet']['edges']), 1)
        self.assertEqual(edges[0]['node']['dataelementSet']['edges'][0]['node']['name'], 'Test Data Element')

    def test_query_related_m2m(self):

        rr = mdr_models.ReviewRequest.objects.create(
            requester=self.editor,
            registration_authority=self.ra,
            status=0,
            state=0,
            registration_date=datetime.date.today(),
            cascade_registration=0
        )

        rr.concepts.add(self.de)
        rr.concepts.add(self.dec)
        rr.concepts.add(self.vd)

        self.login_editor()

        json_response = self.post_query('{ reviewRequests { edges { node { concepts { edges { node { name } } } } } } }')
        edges = json_response['data']['reviewRequests']['edges']
        self.assertEqual(len(edges), 1)

        concept_edges = edges[0]['node']['concepts']['edges']
        self.assertEqual(len(concept_edges), 3)

        item_names = [self.de.name, self.dec.name, self.vd.name]

        for item in concept_edges:
            self.assertTrue(item['node']['name'] in item_names)

    @tag('runthis')
    def test_query_table_inheritance(self):

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

    def test_query_not_allowed_m2m(self):
        # Test accessing an item user doesnt have permission to view through a many to many relation

        self.vd.workgroup = self.wg2
        self.vd.save()

        rr = mdr_models.ReviewRequest.objects.create(
            requester=self.editor,
            registration_authority=self.ra,
            status=0,
            state=0,
            registration_date=datetime.date.today(),
            cascade_registration=0
        )

        rr.concepts.add(self.de)
        rr.concepts.add(self.dec)
        rr.concepts.add(self.vd)

        self.login_editor()

        json_response = self.post_query('{ reviewRequests { edges { node { concepts { edges { node { name } } } } } } }')
        edges = json_response['data']['reviewRequests']['edges']
        self.assertEqual(len(edges), 1)

        concept_edges = edges[0]['node']['concepts']['edges']
        self.assertEqual(len(concept_edges), 2)

        for item in concept_edges:
            self.assertNotEqual(item['node']['name'], 'Test Value Domain')

    def test_reviewrequest_query_perms(self):

        allowed_rr = mdr_models.ReviewRequest.objects.create(
            requester=self.editor,
            registration_authority=self.ra,
            status=0,
            state=1,
            registration_date=datetime.date.today(),
            cascade_registration=0
        )

        disallowed_rr = mdr_models.ReviewRequest.objects.create(
            requester=self.viewer,
            registration_authority=self.ra,
            status=0,
            state=0,
            registration_date=datetime.date.today(),
            cascade_registration=0
        )

        self.login_editor()

        json_response = self.post_query('{ reviewRequests { edges { node { id state } } } }')
        edges = json_response['data']['reviewRequests']['edges']

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['state'], 'A_1')

    def test_query_non_registered_item(self):
        # Test requesting an object without a defined node e.g. User

        json_response = self.post_query('{ metadata { submitter } }', 400)
        self.assertTrue('errors' in json_response.keys())
        self.assertFalse('data' in json_response.keys())
