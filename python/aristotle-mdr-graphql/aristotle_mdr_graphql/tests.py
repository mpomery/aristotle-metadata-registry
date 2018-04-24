from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse
from aristotle_mdr.tests import utils
from aristotle_mdr import models as mdr_models

import json
import datetime

class BaseGraphqlTestCase(utils.LoggedInViewPages):

    def setUp(self):

        super().setUp()
        self.client = Client()
        self.apiurl = reverse('aristotle_graphql:graphql_api')

    def post_query(self, qstring, expected_code=200):
        postdata = {
            'query': qstring
        }

        jsondata = json.dumps(postdata)
        response = self.client.post(self.apiurl, jsondata, 'application/json')
        self.assertEqual(response.status_code, expected_code)
        response_json = json.loads(response.content)
        return response_json

@override_settings(SECURE_SSL_REDIRECT=False)
class GraphqlFunctionalTests(BaseGraphqlTestCase, TestCase):

    def test_get_metadata(self):
        mdr_models.ObjectClass.objects.create(
            name="Test Object Class",
            definition="test defn",
            workgroup=self.wg1
        )

        self.login_editor()
        response_json = self.post_query('{ metadata { edges { node { name } } } }')
        self.assertEqual(response_json['data']['metadata']['edges'][0]['node']['name'], 'Test Object Class')

    def test_load_graphiql(self):

        self.login_editor()

        response = self.client.get(self.apiurl, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('graphene/graphiql.html')

@override_settings(SECURE_SSL_REDIRECT=False)
class GraphqlPermissionsTests(BaseGraphqlTestCase, TestCase):

    def setUp(self):

        super().setUp()

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

    def test_non_registered_item(self):
        # Test requesting an object without a defined node e.g. User

        json_response = self.post_query('{ metadata { submitter } }', 400)
        self.assertTrue('errors' in json_response.keys())
        self.assertFalse('data' in json_response.keys())
