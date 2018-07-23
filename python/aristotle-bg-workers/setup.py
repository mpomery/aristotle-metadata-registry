import os
from setuptools import setup, find_packages

__version__ = '0.3.1'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='aristotle-bg-workers',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    description='Aristotle background workers',
    long_description='Aristotle background workers',
    author='Samuel Spencer',
    author_email='sam@aristotlemetadata.com',
    zip_safe=False,
    install_requires=[
        'celery',
        'django-celery-results'
    ]
)
