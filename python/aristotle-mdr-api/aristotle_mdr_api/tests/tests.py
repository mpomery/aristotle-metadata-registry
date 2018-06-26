from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse

from aristotle_mdr.tests import utils
from aristotle_mdr_api.token_auth.models import AristotleToken
from aristotle_mdr import models
from aristotle_mdr.contrib.slots.tests import BaseSlotsTestCase

from rest_framework.test import APIClient

import json


class TokenTestCase(utils.LoggedInViewPages, TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.apiclient = APIClient()

        self.all_false_perms =  {
            'metadata': {
                'read': False,
                'write': False
            },
            'search': {
                'read': False
            },
            'organization': {
                'read': False
            },
            'ra': {
                'read': False
            }
        }

        self.all_true_perms =  {
            'metadata': {
                'read': True,
                'write': True
            },
            'search': {
                'read': True
            },
            'organization': {
                'read': True
            },
            'ra': {
                'read': True
            }
        }

        self.versions = ['v2', 'v3']

    # ------ Util Functions ------

    def post_token_create(self, name, perms):

        postdata = {'name': name, 'perm_json': json.dumps(perms)}
        response = self.client.post(reverse('token_auth:token_create'), postdata)
        return response

    def get_token(self, name, perms):

        response = self.post_token_create(name, perms)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('key' in response.context.keys())
        return response.context['key']

    def get_user_a_token(self, user, name='User Token'):
        token = AristotleToken.objects.create(
            name=name,
            user=user,
            permissions=self.all_true_perms
        )
        return token

    def get_editor_a_token(self):
        return self.get_user_a_token(self.editor, 'Editor Token')

    # ------ Tests ------

    def test_create_token(self):

        response = self.client.get(reverse('token_auth:token_create'))
        self.assertEqual(response.status_code, 302)

        self.login_viewer()

        self.assertEqual(AristotleToken.objects.count(), 0)
        response = self.client.get(reverse('token_auth:token_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token_create.html')

        perms = self.all_false_perms

        perms['metadata']['read'] = True
        perms['search']['read'] = True
        perms['organization']['read'] = True
        perms['ra']['read'] = True

        token_key = self.get_token('MyToken', perms)
        self.assertEqual(AristotleToken.objects.count(), 1)

        token_obj = AristotleToken.objects.get(key=token_key)
        self.assertEqual(token_obj.permissions, perms)
        self.assertEqual(token_obj.name, 'MyToken')
        self.assertEqual(token_obj.user, self.viewer)
        self.assertIsNotNone(token_obj.key)
        self.assertIsNotNone(token_obj.id)

    def test_delete_token(self):

        editor_token = self.get_editor_a_token()

        self.login_viewer()

        token_key = self.get_token('Brand New Token', self.all_true_perms)
        token_obj = AristotleToken.objects.get(key=token_key)
        token_id = token_obj.id

        delete_url = reverse('token_auth:token_delete', args=[token_id])

        # Check delete confirm page loads
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token_delete.html')

        # Check object can be deleted
        post_response = self.client.post(delete_url, {})
        self.assertRedirects(post_response, reverse('token_auth:token_list'))
        self.assertFalse(AristotleToken.objects.filter(id=token_id).exists())

        # Check user cannot delete a non owned token
        bad_delete_url = reverse('token_auth:token_delete', args=[editor_token.id])
        post_response = self.client.post(bad_delete_url, {})
        self.assertEqual(post_response.status_code, 404)

    def test_update_token(self):

        editor_token = self.get_editor_a_token()

        self.login_viewer()
        token_key = self.get_token('Real Neat Token', self.all_true_perms)
        token_obj = AristotleToken.objects.get(key=token_key)
        token_id = token_obj.id
        initial_perms = token_obj.permissions

        update_url = reverse('token_auth:token_update', args=[token_id])

        # Check initial form data
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token_create.html')

        self.assertTrue(response.context['display_regenerate'])
        self.assertEqual(response.context['form'].initial['perm_json'], json.dumps(initial_perms))
        self.assertEqual(response.context['form'].initial['name'], 'Real Neat Token')

        # Check token object updated on post
        perms = self.all_true_perms
        perms['metadata']['read'] = False

        post_response = self.client.post(update_url, {'name': 'My Updated Token', 'perm_json': json.dumps(perms)})
        self.assertEqual(post_response.status_code, 200)
        self.assertTemplateUsed('aristotle_mdr_api/token_create.html')
        self.assertFalse('key' in post_response.context)
        self.assertTrue('message' in post_response.context)

        updated_token = AristotleToken.objects.get(id=token_id)
        self.assertEqual(updated_token.key, token_key)
        self.assertEqual(updated_token.permissions['metadata']['read'], False)
        self.assertEqual(updated_token.name, 'My Updated Token')

        # Check updating another users token isnt allowed
        bad_update_url = reverse('token_auth:token_update', args=[editor_token.id])

        response = self.client.get(bad_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('aristotle_mdr_api/token_create.html')
        self.assertTrue('error' in response.context)
        self.assertFalse('display_regenerate' in response.context)

        post_response = self.client.post(bad_update_url, {'name': 'Useless Token', 'perm_json': json.dumps(self.all_false_perms)})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('aristotle_mdr_api/token_create.html')
        self.assertTrue('error' in response.context)
        self.assertFalse('display_regenerate' in response.context)

    def test_regenerate_token(self):

        editor_token = self.get_editor_a_token()

        self.login_viewer()
        token_key = self.get_token('Forgotten Token', self.all_true_perms)
        token_obj = AristotleToken.objects.get(key=token_key)
        token_id = token_obj.id

        # Test regenerating a token
        reg_url = reverse('token_auth:token_regenerate', args=[token_id])
        response = self.client.get(reg_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token_create.html')
        self.assertTrue('key' in response.context)
        self.assertNotEqual(response.context['key'], token_key)

        regenerated_token = AristotleToken.objects.get(key=response.context['key'])
        self.assertEqual(regenerated_token.name, 'Forgotten Token')

        # Test user cannot regenerate a token that aint theirs
        bad_reg_url = reverse('token_auth:token_regenerate', args=[editor_token.id])
        response = self.client.get(bad_reg_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('error' in response.context)
        self.assertFalse('key' in response.context)

    def test_list_tokens(self):

        editor_token = self.get_editor_a_token()

        self.login_viewer()

        token_key_1 = self.get_token('My First Token', self.all_true_perms)
        token_key_2 = self.get_token('My Second Token', self.all_true_perms)

        self.assertEqual(AristotleToken.objects.count(), 3)

        listurl = reverse('token_auth:token_list')

        # Test page load
        response = self.client.get(listurl)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token.html')

        # Test only shown your own tokens
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 2)
        self.assertEqual(object_list[0].name, 'My First Token')
        self.assertEqual(object_list[1].name, 'My Second Token')

    @tag('perms')
    def test_token_perms(self):

        self.login_viewer()

        perms = self.all_false_perms

        perms['metadata']['read'] = True
        perms['ra']['read'] = True
        perms['metadata']['write'] = True

        token = self.get_token('MyToken', perms)

        self.client.logout()

        auth = 'Token {}'.format(token)

        # Test that only the endpoints we have perms for are accessable. Anything else should 403
        # HTTP 403 is Authorized but not able to fulfill request'

        for version in self.versions:
            response = self.client.get('/api/' + version + '/metadata/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 200)

            response = self.client.post('/api/' + version + '/metadata/', {}, HTTP_AUTHORIZATION=auth)
            if version == 'v2':
                self.assertEqual(response.status_code, 405) # Write not allowed on v2
            else:
                self.assertEqual(response.status_code, 200)

            response = self.client.get('/api/' + version + '/search/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/api/' + version + '/organizations/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/api/' + version + '/ras/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 200)

            # Types read access is always allowed
            response = self.client.get('/api/v3/types/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 200)

        # Update the tokens permissions

        token_obj = AristotleToken.objects.get(key=token)
        perms['metadata']['write'] = False
        perms['organization']['read'] = True
        perms['ra']['read'] = False
        token_obj.permissions = perms
        token_obj.save()

        # Test the changes are reflected in access

        for version in self.versions:
            response = self.client.post('/api/' + version + '/metadata/', {}, HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/api/' + version + '/organizations/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 200)

            response = self.client.get('/api/' + version + '/ras/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 403)

    @tag('perms')
    def test_invalid_token_perms(self):

        self.client.logout()
        auth = 'Token {}'.format('let_me_in_plz_this_is_a_real_token')

        # Test API Access (HTTP 401 is Unauthorized)
        for version in self.versions:
            response = self.client.get('/api/' + version + '/metadata/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 401)

            response = self.client.post('/api/' + version + '/metadata/', {}, HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 401)

            response = self.client.get('/api/' + version + '/search/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 401)

            response = self.client.get('/api/' + version + '/organizations/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 401)

            response = self.client.get('/api/' + version + '/ras/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 401)

            response = self.client.get('/api/' + version + '/types/', HTTP_AUTHORIZATION=auth)
            self.assertEqual(response.status_code, 401)

    @tag('perms', 'createtest')
    def test_create_metadata_perms(self):

        editor_token = self.get_editor_a_token()
        auth = 'Token {}'.format(editor_token.key)

        self.login_editor()

        # Test post with session auth
        response = self.client.post('/api/v3/metadata/', {})
        self.assertEqual(response.status_code, 403)

        self.client.logout()

        metadata = {
            'concept_type': {
                'app': 'aristotle_mdr',
                'model': 'objectclass'
            },
            'fields': {
                'name': 'Spicy Meatball',
                'definition': 'Very Spicy',
                'workgroup': str(self.wg1.uuid)
            }
        }

        # Post correct data with token auth
        response = self.client.post('/api/v3/metadata/?explode=1', json.dumps(metadata), content_type="application/json", HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content['created']), 1)
        self.assertEqual(len(content['errors']), 0)

        oc = models.ObjectClass.objects.get(uuid=content['created'][0]['uuid'])
        self.assertEqual(oc.name, 'Spicy Meatball')
        self.assertEqual(oc.definition, 'Very Spicy')
        self.assertEqual(oc.workgroup, self.wg1)

        # Attempt to add item to a workgroup without proper perms
        viewer_token = self.get_user_a_token(self.viewer)
        auth = 'Token {}'.format(viewer_token.key)

        response = self.client.post('/api/v3/metadata/?explode=1', json.dumps(metadata), content_type="application/json", HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content['created']), 0)
        self.assertEqual(len(content['errors']), 1)
        print(content['errors'][0]['message'])
        self.assertTrue('You don\'t have permission' in content['errors'][0]['message'])
        self.assertTrue('Test WG 1 Workgroup' in content['errors'][0]['message'])


class SlotTestCase(BaseSlotsTestCase, TestCase):

    def test_slot_view_perms_api(self):
        # Test slot permissions on apis

        self.make_newoc_public()

        for version in ['v2', 'v3']:
            self.client.logout()
            url = '/api/' + version + '/metadata/' + str(self.newoc.uuid) + '/?format=json'
            response = self.client.get(url)
            self.assertEqual(response.status_code, 401)

            self.login_regular_user()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.content)
            self.assertEqual(len(response_data['slots']), 2)
            slots_names = [slot['name'] for slot in response_data['slots']]
            self.assertTrue('public' in slots_names)
            self.assertTrue('auth' in slots_names)

            self.client.logout()
            self.login_editor()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.content)
            self.assertEqual(len(response_data['slots']), 3)
            slots_names = [slot['name'] for slot in response_data['slots']]
            self.assertTrue('public' in slots_names)
            self.assertTrue('auth' in slots_names)
            self.assertTrue('work' in slots_names)
