=====
Comet Indicator Registry (Comet-IR)
=====

The Comet Indicator Registry is an open-source extension for the
`Aristotle Metadata Registry <https://github.com/LegoStormtroopr/aristotle-metadata-registry/>`_
that extends the information model of the ISO/IEC 11179:2013 specification to support the
specialised needs of health management registries.

Comet adds the following administered items:

* Data Sources
* Indicators
* Indicator Sets
* Outcome Areas
* Quality Statements

Comet also adds the following non-administered items:

* Frameworks


Quick start
-----------

1. Add "comet" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'aristotle_mdr',
        'comet',
        ...
    )

   As To ensure that search indexing works properly `haystack` **must** be installed before `aristotle_mdr`.
   If you want to take advantage of Aristotle's access-key shortcut improvements for the admin interface,
   make sure it is installed *before* `grappelli`.

   Comet Indicator Registry adds a replacement templates for some 11179 Objects, such as Data Elements, to show
   associated indicator and related data information on standard Aristotle pages.
   For these overrides to be active, Comet must be installed before aristotle like this::

    INSTALLED_APPS = (
        ...
        'comet',
        'aristotle_mdr',
        '...',
    )


2. Include the Comet and Aristotle URLconfs in your project urls.py like this::

    url(r'^comet/', include('comet.urls')),
    url(r'^/', include('aristotle_mdr.urls')),

3. Run `python manage.py migrate` to create the Comet Database.

4. Start the development server and visit http://127.0.0.1:8000/
   to see the home page.
