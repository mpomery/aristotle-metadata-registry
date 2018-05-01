from aristotle_mdr.tests.settings.settings import *

INSTALLED_APPS = (
    'aristotle_dse',
    'comet',
    'aristotle_mdr_graphql'
) + INSTALLED_APPS

ROOT_URLCONF = 'aristotle_mdr_graphql.tests.urls'
