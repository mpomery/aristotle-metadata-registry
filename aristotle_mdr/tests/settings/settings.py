import os
import sys
from aristotle_mdr.required_settings import *

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)),'..')

sys.path.insert(1, BASE)
sys.path.insert(1, os.path.join(BASE, "tests"))
sys.path.insert(1, os.path.join(BASE, "tests/apps"))
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'tests/apps/bulk_actions_test/templates')
]

SECRET_KEY = 'inara+vtkprm7@0(fsc$+grbz9-s+tmo9d)e#k(9uf8m281&$7xhdkjr'
SOUTH_TESTS_MIGRATE = True

MEDIA_ROOT = os.path.join(BASE, "media")
MEDIA_URL = '/media/'
CKEDITOR_UPLOAD_PATH = 'uploads/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test_database',
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'aristotle_mdr.contrib.search_backends.facetted_whoosh.FixedWhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'aristotle_mdr/tests/whoosh_index'),
        'INCLUDE_SPELLING': True,
    },
}

if 'TRAVIS' in os.environ:
    if os.environ.get('DB') == 'sqlitefile':
        print("Running TRAVIS-CI test-suite with file-based SQLite")
        from aristotle_mdr.tests.settings.templates.db.sqlite import DATABASES
    elif os.environ.get('DB') == 'postgres':
        print("Running TRAVIS-CI test-suite with POSTGRESQL")
        from aristotle_mdr.tests.settings.templates.db.postgres import DATABASES
    elif os.environ.get('DB') == 'mysql':
        print("Running TRAVIS-CI test-suite with MySQL")
        from aristotle_mdr.tests.settings.templates.db.mysql import DATABASES

    if os.environ.get('SEARCH') == 'whoosh':
        print("Running TRAVIS-CI test-suite with whoosh")
        if os.environ.get('VARIANT') == 'haystack':
            print("Vanilla haystack variant")
            from aristotle_mdr.tests.settings.templates.search.haystack_whoosh import HAYSTACK_CONNECTIONS
        else:
            print("Aristotle specific variant")
            from aristotle_mdr.tests.settings.templates.search.whoosh import HAYSTACK_CONNECTIONS
    elif os.environ.get('SEARCH') == 'elasticsearch':
        print("Running TRAVIS-CI test-suite with elasticsearch")
        if os.environ.get('VARIANT') == 'haystack':
            print("Vanilla haystack variant")
            from aristotle_mdr.tests.settings.templates.search.haystack_elasticsearch import HAYSTACK_CONNECTIONS
        else:
            print("Aristotle specific variant")
            from aristotle_mdr.tests.settings.templates.search.elasticsearch import HAYSTACK_CONNECTIONS

if 'ARISTOTLE_DEV_SKIP_MIGRATIONS' in os.environ or os.environ.get('DB') == 'mysql':  # pragma: no cover
    print("Skipping migrations")
    class DisableMigrations(object):
    
        def __contains__(self, item):
            return True
    
        def __getitem__(self, item):
            return "notmigrations"
    
    MIGRATION_MODULES = DisableMigrations()


INSTALLED_APPS = (
    # The good stuff
    'aristotle_mdr.contrib.self_publish',
    'templatetags',
    'extension_test',
    'text_download_test',
) + INSTALLED_APPS


# https://docs.djangoproject.com/en/1.6/topics/testing/overview/#speeding-up-the-tests
# We do a lot of user log in testing, this should speed stuff up.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

ARISTOTLE_SETTINGS['SEPARATORS']['DataElementConcept'] = '--'
ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] = ARISTOTLE_SETTINGS['CONTENT_EXTENSIONS'] + ['extension_test']
ARISTOTLE_DOWNLOADS = ARISTOTLE_DOWNLOADS + [
    ('txt', 'Text', 'fa-file-pdf-o', 'text_download_test'),
]
ARISTOTLE_SETTINGS['BULK_ACTIONS'].update({
    'quick_pdf_download':'aristotle_mdr.forms.bulk_actions.QuickPDFDownloadForm',
    'delete': 'bulk_actions_test.actions.StaffDeleteActionForm',
    'incomplete': 'bulk_actions_test.actions.IncompleteActionForm',
})
ROOT_URLCONF = 'extension_test.urls'

# disable
__LOGGING__ = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console-simple': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
            },
        },
    'loggers': {
        'aristotle_mdr': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
            },
        'django': {
            'handlers': ['console-simple'],
            'level': 'INFO',
            'propagate': True,
            },
        }
    }

