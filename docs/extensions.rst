.. _extensions:

Extensions
==========

Confab supports specifying extra paths to templates and data directories via a
'confab.extensions' distribution entry point.

An extension entry point must point to a callable that returns the base path
to the data and templates directories::

    entry_points={
        'confab.extensions': [
            'mydist = mydist.module_with:path_to_directories',
        ],
    },
