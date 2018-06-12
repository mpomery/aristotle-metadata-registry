from aristotle_mdr.tests.settings.settings import *
from aristotle_mdr_api.settings import SERIALIZATION_MODULES, REST_FRAMEWORK, REQUIRED_APPS as API_REQUIRED_APPS

import os

INSTALLED_APPS = INSTALLED_APPS + API_REQUIRED_APPS

ROOT_URLCONF = 'aristotle_mdr_api.tests.urls'

PACKAGE_DIR = os.path.dirname(os.path.dirname(__file__))

STATICFILES_DIRS = [
    os.path.join(PACKAGE_DIR, 'static')
]

STATIC_ROOT = '/tmp/staticfiles'
