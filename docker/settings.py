"""
Base settings necessary for running an Aristotle Instance in "the cloud (tm)"
"""

from aristotle_mdr.required_settings import *

ALLOWED_HOSTS = ["*"]
DEBUG = True
ARISTOTLE_SETTINGS['SITE_NAME'] = 'Aristotle Development Server'
