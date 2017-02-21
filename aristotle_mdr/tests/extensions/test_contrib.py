import os

from aristotle_mdr.contrib.browse.tests.test_browse import *
from aristotle_mdr.contrib.generic.tests import *
from aristotle_mdr.contrib.help.tests import *
from aristotle_mdr.contrib.self_publish.tests import *
if os.environ.get('DB') != 'mysql':
    from aristotle_mdr.contrib.slots.tests import *
from aristotle_mdr.contrib.identifiers.tests import *
from aristotle_mdr.contrib.healthcheck.tests import *
