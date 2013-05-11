.. _usage:

Usage
=====

Confab may be used in several ways.

.. _usage_confab:

Via ``confab`` – The Default Console Script
-------------------------------------------

The distribution ships with the ``confab`` console script, which provides a
simple command line usage based on common defaults::

    confab -d /path/to/directory -H hosts -u user <command>

Confab then loads its definitions, configuration data, and templates from within
the provided directory as follows::

    /path/to/directory/settings.py            # definitions
    /path/to/directory/templates/{component}/ # templates for {component}
    /path/to/directory/data/default.py        # default configuration data
    /path/to/directory/data/{environment}.py  # per-environment configuration data
    /path/to/directory/data/{role}.py         # per-role configuration data
    /path/to/directory/data/{component}.py    # per-component configuration data
    /path/to/directory/data/{host}.py         # per-host configuration data
    /path/to/directory/generated/{hostname}/  # generated configuration files for hostname
    /path/to/directory/remotes/{hostname}/    # copies of remote configuration files from hostname

.. _usage-fabfile:

Via Inclusion in a ``fabfile``
------------------------------

Confab's tasks may be included in another fabfile simply by adding::

    from confab.api import *

And then running::

    fab <task>:<arguments>

When invoking Confab tasks from *fab*, configuration directories must be provided
as task arguments.

To specify :term:`roles<role>` and :term:`environments<environment>` to
customize configuration data, the fabfile can use the :mod:`~confab.autotasks`,
for example::

    from confab.api import *
    from confab.autotasks import autogenerate_tasks

    # load roledefs and environmentdefs from settings.py
    load_model_from_dir('/path/to/directory')
    # create tasks for each defined role and environment
    autogenerate_tasks()

Autotasks would then allow fab to run as::

    fab role_{role} env_{environment} <task>:arguments

Via the API
-----------

Confab's lower level :ref:`API<api>` can be invoked using customized data
loading functions, either to create new tasks or to be called directly from
a new console script::

    from confab.api import ConfFiles

    conffiles = ConfFiles(jinja2_environment_loader, data_loader)
