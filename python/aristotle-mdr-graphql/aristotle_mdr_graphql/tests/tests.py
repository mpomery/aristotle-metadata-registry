from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse
from aristotle_mdr.tests import utils
from aristotle_mdr import models as mdr_models
from aristotle_dse import models as dse_models
from aristotle_mdr.contrib.slots import models as slots_models
from aristotle_mdr.contrib.identifiers import models as ident_models
from aristotle_mdr.contrib.slots.tests import BaseSlotsTestCase
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

    def test_query_icontains(self):

        self.login_editor()
        response_json = self.post_query('{ metadata (name_Icontains: \"object\") { edges { node { name } } } }')
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

        mdr_models.DedInputsThrough.objects.create(
            data_element_derivation=ded,
            data_element=self.de,
            order=0
        )

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

    def test_query_slots_identifiers(self):

        self.login_editor()

        # Add slot
        slot = slots_models.Slot.objects.create(
            name='Test slot',
            concept=self.oc,
            value='Test Value',
            permission=0
        )

        # Add identifier
        ra = mdr_models.RegistrationAuthority.objects.create()
        namespace = ident_models.Namespace.objects.create(
            naming_authority=ra,
            shorthand_prefix='pre'
        )
        ident = ident_models.ScopedIdentifier.objects.create(
            namespace=namespace,
            concept=self.oc,
            identifier='Test Identifier',
            version='1.0.1'
        )

        self.assertEqual(self.oc.identifiers.count(), 1)
        self.assertEqual(self.oc.slots.count(), 1)

        querytext = (
            '{ metadata (name: "Test Object Class") { edges { node { name slots { edges { node { name } } }'
            ' identifiers { identifier } } } } }'
        )

        json_response = self.post_query(querytext)
        edges = json_response['data']['metadata']['edges']
        self.assertEqual(edges[0]['node']['slots']['edges'][0]['node']['name'], 'Test slot')
        self.assertEqual(edges[0]['node']['identifiers'][0]['identifier'], 'Test Identifier')

    def test_identifier_filters(self):

        self.login_editor()

        # Add identifier
        ra = mdr_models.RegistrationAuthority.objects.create()
        namespace = ident_models.Namespace.objects.create(
            naming_authority=ra,
            shorthand_prefix='pre'
        )
        ident = ident_models.ScopedIdentifier.objects.create(
            namespace=namespace,
            concept=self.oc,
            identifier='Test Identifier',
            version='1.0.1'
        )
        other_ident = ident_models.ScopedIdentifier.objects.create(
            namespace=namespace,
            concept=self.de,
            identifier='ZZZ',
            version='6.6.6'
        )

        self.assertEqual(self.oc.identifiers.count(), 1)

        # Identifier filter
        json_response = self.post_query(
            '{{ metadata (identifier: "{}") {{ edges {{ node {{ name }} }} }} }}'.format(ident.identifier)
        )
        edges = json_response['data']['metadata']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Object Class')

        # Identifier Version filter
        json_response = self.post_query(
            '{{ metadata (identifierVersion: "{}") {{ edges {{ node {{ name }} }} }} }}'.format(ident.version)
        )
        edges = json_response['data']['metadata']['edges']
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['node']['name'], 'Test Object Class')

        # Identifier Namespace filter
        json_response = self.post_query(
            '{{ metadata (identifierNamespace: "{}") {{ edges {{ node {{ name }} }} }} }}'.format(namespace.shorthand_prefix)
        )
        edges = json_response['data']['metadata']['edges']
        self.assertEqual(len(edges), 2)

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


class GraphqlSlotsTests(BaseSlotsTestCase, BaseGraphqlTestCase, TestCase):

    def check_slots(self, gql_response, slots):
        slots_edges = gql_response['data']['metadata']['edges'][0]['node']['slots']['edges']
        self.assertEqual(len(slots_edges), len(slots))

        returned_slots = [edge['node']['name'] for edge in slots_edges]

        for slot in slots:
            self.assertTrue(slot in returned_slots)

    def test_graphql_slots(self):

        self.make_newoc_public()

        # Test query anon
        self.client.logout()
        query = '{ metadata (name: "testoc") { edges { node { slots { edges { node { name } } } } } } }'
        json_response = self.post_query(query, 200)
        self.check_slots(json_response, ['public'])

        # Test query auth
        self.client.logout()
        self.login_regular_user()
        json_response = self.post_query(query, 200)
        self.check_slots(json_response, ['public', 'auth'])

        # Test query user in wg
        self.client.logout()
        self.login_editor()
        json_response = self.post_query(query, 200)
        self.check_slots(json_response, ['public', 'auth', 'work'])
