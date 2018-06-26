===========================================
Aristotle Metadata Registry (Aristotle-MDR)
===========================================

|aristotle-logo|

|tci-build-status| |docs| |coveralls| |demoserver| |codeclimate| |wcagzoo|

Introduction and mission statement
----------------------------------
Aristotle-MDR is an open-source metadata registry as laid out by the requirements
of the `ISO/IEC 11179:2013 specification <http://metadata-standards.org/11179/>`_.

Aristotle-MDR represents a new way to manage and federate content built on and extending
the principles of leading metadata registries. The code of Aristotle is completely open-source,
building on the Django web framework and the mature model of the 11179 standard, allowing
agencies to easily run their own metadata registries while also having the ability
to extend the information model and tap into the permissions and roles of ISO 11179.

By allowing organisations to run their own independent registries they are able to
expose authoritative metadata along with the governance processes behind its creation,
and by building upon known and open systems agencies, can deliver a stable platform
for the sharing of metadata.

Extensions
++++++++++
Aristotle-MDR aims to be compliant to the core model described within ISO/IEC 11179,
however `a number of extensions are available to extend functionality and add additional content types <https://github.com/aristotle-mdr/aristotle-metadata-registry/wiki/Available-Extensions>`_.


Quick start
-----------

1. Install using the pip package manager::

    pip install aristotle-metadata-registry

#. Aristotle has a large number of requirements, to support search, API, downloads and such, so review `example_mdr/settings.py` to ensure you have all of the right settings applied.

    For installed apps this can be applied like so::

    FROM aristotle_mdr.required_settings import INSTALLED_APPS as ARISTOTLE_APPS
    INSTALLED_APPS = (
        ...
    ) + ARISTOTLE_APPS

   To ensure that search indexing works properly ``haystack`` **must** be installed before `aristotle_mdr`.
   If you want to take advantage of Aristotle's access-key shortcut improvements for the admin interface,
   make sure it is installed *before* the django admin app.

#. Include the Aristotle-MDR URLconf in your project ``urls.py``. Because Aristotle will
   form the majority of the interactions with the site, and the Aristotle includes a
   number of URLconfs for supporting apps its recommended to included it at the
   server root, like this::

    url(r'^/', include('aristotle_mdr.urls')),

#. Run ``python manage.py migrate`` to create the Aristotle-MDR Database.

#. (Optional) Compile the multilingual resource files for improved performance, like so::

     django-admin.py compilemessages

#. Start the development server and visit ``http://127.0.0.1:8000/``
   to see the home page.

For a complete example of how to successfully include Aristotle, see the `tests/settings.py` settings file.

**An open instance of the Aristotle Metadata Registry is available at:** `registry.aristotlemetadata.com <http://registry.aristotlemetadata.com/>`_.


Screenshots for users
---------------------

`More screenshots available in the Aristotle Metadata Registry User Help Documentation <http://help.aristotlemetadata.com/>`_.

A data element shown on desktop and mobile
|homescreenshot|

An item being edited without changing screens
|itemeditsample|

Information for developers
--------------------------

Aristotle-MDR is free open-source software and contributions are welcome on front-end web development,
back-end server development, translation and content creation (such as more documentation).
Review the wiki, open issues and existing documentation to get started.

**If you are looking to contribute**, `a good place to start is checking out the open issues labeled "help wanted" <https://github.com/aristotle-mdr/aristotle-metadata-registry/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22>`_
or reviewing the `documentation <http://aristotle-metadata-registry.readthedocs.org/en/latest/>`_ and `wiki  <https://github.com/aristotle-mdr/aristotle-metadata-registry/wiki>`_ and identifying (and even adding) content that isn't there.

Using docker
++++++++++++

To test Aristotle, there is an included `Dockerfile`. This will:

* Use the `/aristotle_mdr/example_mdr/` django settings file
* Install Aristotle-MDR and all requirements
* Create an SQLite Database and Whoosh search index inside the Container
* Collect the necessary static files
* Load some sample metadata
* Run a server using the django `runserver` management command.

To start this, from the repository directory run::

    docker build . -t aristotle
    docker run -t --name amdr -p 8000:8000 aristotle

Then browse to `localhost:8000` to see the "Example Metadata Registry".

The included `Dockerfile` is for development purposes, and is not suitable for production deployments.


About the badges (plus some extras):
++++++++++++++++++++++++++++++++++++
* |tci-build-status| - Travis-CI, showing the details of the continuous testing suite
* |docs| - Read the docs, with details on installing, configuring and extending Aristotle-MDR
* |coveralls| - Coveralls, showing in-depth code coverage
* |codecov| - Codecov.io, showing even greater in-depth code coverage with branch coverage
* |demoserver| - A link to a live open-metadata registry
* |gitter| - Gitter, a git-powered chat room for developers
* |waffleio| - Waffle.io bugs ready to be actioned.
* |codeclimate| - Code Climate - additional code metrics
* |wcagzoo| - Web Content Accessibility Guidelines AA Compliant

.. |tci-build-status| image:: https://travis-ci.org/aristotle-mdr/aristotle-metadata-registry.svg?branch=master
    :alt: Travis-CI build status
    :scale: 100%
    :target: https://travis-ci.org/aristotle-mdr/aristotle-metadata-registry

.. |docs| image:: https://readthedocs.org/projects/aristotle-metadata-registry/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/aristotle-metadata-registry/

.. |coveralls| image:: https://coveralls.io/repos/aristotle-mdr/aristotle-metadata-registry/badge.png?branch=master
    :alt: Code coverage on coveralls
    :scale: 100%
    :target: https://coveralls.io/r/aristotle-mdr/aristotle-metadata-registry?branch=master

.. |codecov| image:: https://codecov.io/github/aristotle-mdr/aristotle-metadata-registry/coverage.svg?branch=master
    :alt: Code coverage on code cov (includes branch checks)
    :scale: 100%
    :target: https://codecov.io/github/aristotle-mdr/aristotle-metadata-registry?branch=master

.. |demoserver| image:: https://img.shields.io/badge/Open_Metadata_Registry-online-blue.svg
    :alt: visit the open access metadata registry
    :scale: 98%
    :target: https://registry.aristotlemetadata.com

.. |gitter| image:: https://badges.gitter.im/Join%20Chat.svg
    :alt: visit the gitter chat room for this project
    :scale: 100%
    :target: https://gitter.im/LegoStormtroopr/aristotle-metadata-registry?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge

.. |waffleio| image:: https://badge.waffle.io/aristotle-mdr/aristotle-metadata-registry.png?label=ready&title=Ready 
    :target: https://waffle.io/aristotle-mdr/aristotle-metadata-registry 
    :alt: 'Stories in Ready'

.. |codeclimate| image:: https://codeclimate.com/github/aristotle-mdr/aristotle-metadata-registry/badges/gpa.svg
   :target: https://codeclimate.com/github/aristotle-mdr/aristotle-metadata-registry
   :alt: Code Climate

.. |wcagzoo| image:: https://img.shields.io/badge/WCAG_Zoo-AA-green.svg
   :target: https://github.com/data61/wcag-zoo/wiki/Compliance-Statement
   :alt: This repository is WCAG-Zoo compliant

.. |homescreenshot| image:: https://user-images.githubusercontent.com/2173174/28704337-3a65dbca-73ad-11e7-9d01-fce46591118a.png
    :alt:  Main screen of the Aristotle registry
    :scale: 100%

.. |newitemsample| image:: https://user-images.githubusercontent.com/2173174/28704337-3a65dbca-73ad-11e7-9d01-fce46591118a.png
    :alt:  Data Element on desktop and mobile
    :scale: 100%

.. |itemeditsample| image:: https://user-images.githubusercontent.com/2173174/28704593-be870022-73ae-11e7-8ff8-5c328fe28281.png
    :alt: Edit screen for a metadata object
    :scale: 100%

.. |aristotle-logo| image:: https://raw.githubusercontent.com/aristotle-mdr/aristotle-metadata-registry/develop/aristotle_mdr/static/aristotle_mdr/images/aristotle.png
    :alt: Aristotle-MDR Logo
    :scale: 100%
    :target: http://www.aristotlemetadata.com
