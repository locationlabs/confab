.. _configuration-data:

Configuration Data
==================

Configuration data is loaded from python modules named after the names of the
selected environment, role, component, and host, plus a standard set of defaults.
The dictionaries from these modules (if any) are recursively merged (see below),
so that given an environment named "foo", a role named "bar", a component named
"baz", and a host named "host", the configuration data would be merged between
**default.py**, **foo.py**, **bar.py**, **baz.py**, and **host.py**.

Confab uses the *__dict__* property of the loaded module, but filters out any
entries starting with '_'. In other words, this module::

    foo = 'bar'
    _ignore = 'this'

results in this dictionary::

    {'foo': 'bar'}

If a configuration data module is not found, Confab will also look for a file
with a `.py_tmpl` suffix and treat it as a Jinja2 template for the same module,
allowing configuration data to use Jinja2 template syntax (including includes).

Confab expects roles, environments, and definitions thereof to be saved in the
Fabric environment.  The *confab* console script requires these definitions,
although the lower level API is designed to be tolerant of these values being
absent.  Both the console script and the lower level API require that the
current host be defined in Fabric's *env.host_string*.

Merging Strategy
----------------

By default, Confab recursively merges configuration dictionaries from various
sources, using a three level hierarchy:

 -  Host-specific values are used first.
 -  Environment-specific values are used next.
 -  Role or component-specific values are used next.
 -  Default values are used last.

Confab's recursive merge operation can be futher customized by using callable
wrappers around configuration values.  Confab will always delegate to a callable
to define how values are overriden, e.g. allowing lists values to be
appended/prepended to default values.

