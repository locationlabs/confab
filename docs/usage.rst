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

.. _usage_fabfile:

Via Inclusion in a ``fabfile``
------------------------------

Confab's tasks may be included in another fabfile simply by adding::

    from confab.api import diff, generate, generate_tasks, pull, push

    # generate environment tasks
    generate_tasks('/path/to/settings')

And then running::

    fab <env_name>:{role1},{role2} <task>:<arguments>

Note that the settings path, roles list, and arguments are optional.

Via the API
-----------

Confab's lower level :ref:`API<api>` can be invoked directly either to create
new tasks or as part of some other script::

    from confab.api import *
    from confab.autotasks import generate_tasks

    # load roledefs and environmentdefs from settings.py
    load_model_from_dir('/path/to/directory')
    # create tasks for each defined role and environment
    generate_tasks()

Autotasks would then allow fab to run as::

    fab role_{role} env_{environment} <task>:arguments

Confab's lower level API can also be invoked using customized data loading
functions, either to create new tasks or to be called directly from a new
console script.
