import os
from setuptools import setup, find_packages
from setuptools.command.install import install

__version__ = '0.1.0'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

import subprocess

class InstallLocalPackages(install):
    def run(self):

        install.run(self)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        py_path = os.path.join(this_dir, "python")

        for d in os.listdir(py_path):
            print( os.path.join(py_path, d))
            cmd = ["python", '%s/setup.py'%os.path.join(py_path, d), 'install']
            cmd = ["pip", 'install', '%s'%os.path.join(py_path, d)]
            out = subprocess.call(cmd) #, shell=True)
            if out == 1:
                1/0
            else:
                print("Installed ", py_path)


setup(
    name='plato',
    version=__version__,
    # packages=find_packages(),
    # include_package_data=True,
    license='MIT License',
    description='Plato',
    long_description='Plato',
    url='https://www.aristotlemetadata.com/cloud',
    author='Samuel Spencer',
    author_email='sam@aristotlemetadata.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
    ],
    cmdclass={ 'install': InstallLocalPackages }
)
