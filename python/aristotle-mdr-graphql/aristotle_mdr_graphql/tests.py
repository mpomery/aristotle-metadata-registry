from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse
from aristotle_mdr.tests import utils
from aristotle_mdr import models as mdr_models

import json

class BaseGraphqlTestCase(utils.LoggedInViewPages):

    def setUp(self):

        super().setUp()
        self.client = Client()
        self.apiurl = reverse('aristotle_graphql:graphql_api')

    def post_query(self, qstring):
        postdata = {
            'query': qstring
        }

        jsondata = json.dumps(postdata)
        response = self.client.post(self.apiurl, jsondata, 'application/json')
        self.assertEqual(response.status_code, 200)
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

        self.login_editor()
        json_response = self.post_query('{ metadata { edges { node { name } } } }')
        self.assertEqual(len(json_response['data']['metadata']['edges']), 3)

        json_response = self.post_query('{ dataElements { edges { node { name dataElementConcept { name } valueDomain { name } } } } }')
        edges = json_response['data']['dataElements']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Data Element')
        self.assertEqual(edges[0]['node']['dataElementConcept']['name'], 'Test Data Element Concept')
        self.assertEqual(edges[0]['node']['valueDomain']['name'], 'Test Value Domain')
