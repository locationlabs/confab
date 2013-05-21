.. _data:

Data Loading
============

Configuration data is loaded from python modules named after the selected
:term:`environment`, :term:`role`, :term:`component`, and :term:`host`, plus a
standard set of defaults. For example, if Confab is operating on an environment
named ``foo``, a role named ``bar``, a component named ``baz``, and a host
named ``host``, configuration data would be loaded from ``foo.py``, ``bar.py``,
``baz.py``, ``host.py``, and ``default.py``.

If a configuration data module is not found, Confab will also look for a file
with a ``.py_tmpl`` suffix and treat it as a Jinja2 template for the same
module, allowing configuration data to use Jinja2 template syntax (including
:class:`include<jinja2.nodes.Include>`).

Confab uses the ``__dict__`` property of the loaded module to generate
dictionaries, filtering out any entries starting with ``_``. In other words,
this module::

    foo = 'bar'
    _ignore = 'this'

results in this dictionary::

    {'foo': 'bar'}

The dictionaries from all of the loaded modules (if any) are recursively merged
into a single dictionary, which is then used to populate :ref:`templates`.
Merging operates in the following order:

1.  Host-specific values are used first.
2.  Environment-specific values are used next.
3.  Role or component-specific values are used next.
4.  Default values are used last.

Confab's recursive merge operation can be futher customized by using callable
wrappers around configuration values. Confab will always delegate to a callable
to define how values are overriden, e.g. allowing lists values to be
appended/prepended to default values.
