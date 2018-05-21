from django.test import TestCase, Client, override_settings, tag
from django.urls import reverse

from aristotle_mdr.tests import utils
from aristotle_mdr_api.token_auth.models import AristotleToken

from rest_framework.test import APIClient

import json

@override_settings(SECURE_SSL_REDIRECT=False)
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
                'read': False,
                'write': False
            },
            'ra': {
                'read': False,
                'write': False
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
                'read': True,
                'write': True
            },
            'ra': {
                'read': True,
                'write': True
            }
        }

    # ------ Util Functions ------

    def post_token_create(self, name, perms):

        postdata = {'name': name, 'perm_json': json.dumps(perms)}
        response = self.client.post(reverse('token_create'), postdata)
        return response

    def get_token(self, name, perms):

        response = self.post_token_create(name, perms)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('key' in response.context.keys())
        return response.context['key']

    def get_editor_a_token(self):
        token = AristotleToken.objects.create(
            name='Editor Token',
            user=self.editor,
            permissions=self.all_true_perms
        )
        return token

    # ------ Tests ------

    def test_create_token(self):

        response = self.client.get(reverse('token_create'))
        self.assertEqual(response.status_code, 302)

        self.login_viewer()

        self.assertEqual(AristotleToken.objects.count(), 0)
        response = self.client.get(reverse('token_create'))
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

        delete_url = reverse('token_delete', args=[token_id])

        # Check delete confirm page loads
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token_delete.html')

        # Check object can be deleted
        post_response = self.client.post(delete_url, {})
        self.assertRedirects(post_response, reverse('token_list'))
        self.assertFalse(AristotleToken.objects.filter(id=token_id).exists())

        # Check user cannot delete a non owned token
        bad_delete_url = reverse('token_delete', args=[editor_token.id])
        post_response = self.client.post(bad_delete_url, {})
        self.assertEqual(post_response.status_code, 404)

    def test_update_token(self):

        editor_token = self.get_editor_a_token()

        self.login_viewer()
        token_key = self.get_token('Real Neat Token', self.all_true_perms)
        token_obj = AristotleToken.objects.get(key=token_key)
        token_id = token_obj.id
        initial_perms = token_obj.permissions

        update_url = reverse('token_update', args=[token_id])

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
        self.assertTrue('key' in post_response.context)

        updated_token = AristotleToken.objects.get(id=token_id)
        self.assertEqual(updated_token.key, token_key)
        self.assertEqual(updated_token.permissions['metadata']['read'], False)
        self.assertEqual(updated_token.name, 'My Updated Token')

        # Check updating another users token isnt allowed
        bad_update_url = reverse('token_update', args=[editor_token.id])

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

    @tag('reg')
    def test_regenerate_token(self):

        editor_token = self.get_editor_a_token()

        self.login_viewer()
        token_key = self.get_token('Forgotten Token', self.all_true_perms)
        token_obj = AristotleToken.objects.get(key=token_key)
        token_id = token_obj.id

        # Test regenerating a token
        reg_url = reverse('token_regenerate', args=[token_id])
        response = self.client.get(reg_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr_api/token_create.html')
        self.assertTrue('key' in response.context)
        self.assertNotEqual(response.context['key'], token_key)

        regenerated_token = AristotleToken.objects.get(key=response.context['key'])
        self.assertEqual(regenerated_token.name, 'Forgotten Token')

        # Test user cannot regenerate a token that aint theirs
        bad_reg_url = reverse('token_regenerate', args=[editor_token.id])
        response = self.client.get(bad_reg_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('error' in response.context)
        self.assertFalse('key' in response.context)

    def test_token_perms(self):

        self.login_viewer()

        perms = self.all_false_perms

        perms['metadata']['read'] = True
        perms['ra']['read'] = True

        token = self.get_token('MyToken', perms)

        self.client.logout()

        auth = 'Token {}'.format(token)

        response = self.client.get('/api/v3/metadata/', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v3/search/', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 403)

        response = self.client.get('/api/v3/organizations/', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 403)

        response = self.client.get('/api/v3/ras/', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v3/types/', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)
