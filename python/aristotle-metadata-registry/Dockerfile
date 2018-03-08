FROM python:3
RUN pip install -U setuptools

ADD . /usr/src/app/amdr
ADD ./aristotle_mdr/install/example_mdr /usr/src/app

WORKDIR /usr/src/app/amdr
RUN pip install -r requirements.txt

WORKDIR /usr/src/app
RUN pip install -r requirements.txt

ENV aristotle_mdr__BASEDIR=/usr/src/app
ENV PYTHONPATH=/usr/src/app/amdr:$PYTHONPATH

RUN pip install channels==1.1.5 # Bug with channels in Django < 1.10 See: https://github.com/django/channels/issues/696

RUN DJANGO_SETTINGS_MODULE=example_mdr.settings ./manage.py migrate
RUN DJANGO_SETTINGS_MODULE=example_mdr.settings ./manage.py collectstatic --noinput

RUN DJANGO_SETTINGS_MODULE=example_mdr.settings ./manage.py loaddata system.json
RUN DJANGO_SETTINGS_MODULE=example_mdr.settings ./manage.py loaddata iso_metadata.json
RUN DJANGO_SETTINGS_MODULE=example_mdr.settings ./manage.py loaddata test_metadata.json
RUN DJANGO_SETTINGS_MODULE=example_mdr.settings ./manage.py load_aristotle_help

EXPOSE 8000
CMD ./manage.py runserver 0.0.0.0:8000
