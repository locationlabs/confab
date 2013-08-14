.. _functions:

Functions
---------

Confab provides four basic functions:

 1. It defines a data model where :term:`hosts<host>` belong to one or more
    :term:`environments<environment>` and are assigned to one or more
    :term:`roles<role>`, which can be made up of :term:`components<component>`.

 2. It defines a mechanism for loading configuration data based on a set of
    *defaults* and override values defined per
    :term:`environment`, :term:`host`, :term:`role`, or :term:`component`.

 3. It defines a mechanism for loading Jinja2_ templates for configuration files
    based on a :term:`role` and/or :term:`component`.

 4. It defines Fabric_ tasks to faciliate publishing configuration files
    generated from applying the configuration data to the Jinja2_ templates to
    :term:`hosts<host>`.

Confab's configuration data and :ref:`templates` are expected to be checked in
to version control so that changes to configuration are managed through a
regular versioning and release process.


.. _Fabric: http://docs.fabfile.org/en/1.6/
.. _Jinja2: http://jinja.pocoo.org/docs/
