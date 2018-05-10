from aristotle_mdr.tests.settings.settings import *

INSTALLED_APPS = (
    'aristotle_dse',
    'comet',
    'aristotle_mdr_graphql',
    'graphene_django'
) + INSTALLED_APPS

ROOT_URLCONF = 'aristotle_mdr_graphql.tests.urls'

ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'].append('aristotle_dse')
ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'].append('comet')
