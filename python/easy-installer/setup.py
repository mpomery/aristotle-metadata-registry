import os
from setuptools import setup, find_packages

__version__ = '0.0.1'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='easyinstaller',
    version=__version__,
    packages=['easy_installer'],
    include_package_data=True,
    license='DWTFYW',
    description='Easy',
    long_description='Easy As',
    url='https://www.aristotlemetadata.com/cloud',
    author='Harry White',
    author_email='harry@aristotlemetadata.com',
    zip_safe=False,
    entry_points={
        'console_scripts': ['aristotle-installer=easy_installer.install:main']
    },
    install_requires=[
        'requests'
    ]
)
