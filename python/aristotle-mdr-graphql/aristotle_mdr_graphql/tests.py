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

@override_settings(SECURE_SSL_REDIRECT=False)
class GraphqlFunctionalTests(BaseGraphqlTestCase, TestCase):

    @tag('runthis')
    def test_get_metadata(self):
        mdr_models.ObjectClass.objects.create(
            name="Test Object Class",
            definition="test defn",
            workgroup=self.wg1
        )

        self.login_editor()

        postdata = {
            'query': '{ metadata { edges { node { name } } } }'
        }
        
        jsondata = json.dumps(postdata)
        response = self.client.post(self.apiurl, jsondata, 'application/json')
        self.assertEqual(response.status_code, 200)

        response_json = json.loads(response.content)
        self.assertEqual(response_json['data']['metadata']['edges'][0]['node']['name'], 'Test Object Class')

    def test_load_graphiql(self):

        self.login_editor()

        print(self.apiurl)
        response = self.client.get(self.apiurl, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)

@override_settings(SECURE_SSL_REDIRECT=False)
class GraphqlPermissionsTests(TestCase):
    pass
