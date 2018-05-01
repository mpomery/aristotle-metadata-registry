from aristotle_mdr.tests.settings.settings import *
from aristotle_mdr.required_settings import INSTALLED_APPS

INSTALLED_APPS = (
    'aristotle_dse',
    'comet'
) + INSTALLED_APPS
