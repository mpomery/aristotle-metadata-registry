# Aristotle Development Docker environment

This docker configuration is designed to make development of the Aristotle Metadata Registry
easy and makes it easier to review the system. This docker *should not* be used as the base of
a production instance of Aristotle.

* Step 1: Clone the Aristotle Metadata repository
* Step 2: From this directory run `docker-compose up`
* Step 3: Done!

This will create a docker image, will all components of the registry installed as editable
python modules, ready to run as a web service.
This web service will be run on port 8080 and accept all hosts (`ALLOWED_HOSTS = ['*']`),
and serves static files from app directories thorugh Django - both not recommended for
production.

Running this will create 'docker/data' directory in the repository that will not be checked
in or tracked for changes.

## Running tests in this environment

* Step 1: From this directory run `docker-compose up`
* Step 2: `docker-compose exec web bash`
* Step 3: From this docker bash console execute the desired test. It is recommended that the
  correct `DJANGO_SETTINGS_MODULE` is exported or prefixed in this environment

  For example to run all Aristotle tests, run:

        DJANGO_SETTINGS_MODULE=aristotle_mdr.tests.settings.settings django-admin test aristotle_mdr.tests

  Or to run a single class of tests, run:

        DJANGO_SETTINGS_MODULE=aristotle_mdr.tests.settings.settings django-admin test aristotle_mdr.tests.main.test_html_pages.AnonymousUserViewingThePages
