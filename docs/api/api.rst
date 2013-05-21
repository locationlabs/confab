.. _api_module:

:mod:`confab.api`
-----------------

.. automodule:: confab.api

Core
~~~~

- :class:`~confab.conffiles.ConfFiles`

Settings
~~~~~~~~

- :class:`~confab.definitions.Settings`

Environment Tasks
~~~~~~~~~~~~~~~~~

- :func:`~confab.autotasks.generate_tasks`

Jinja2 Environment Loading
~~~~~~~~~~~~~~~~~~~~~~~~~~

- :class:`~confab.loaders.FileSystemEnvironmentLoader`
- :class:`~confab.loaders.PackageEnvironmentLoader`

Data Loading
~~~~~~~~~~~~

- :class:`~confab.data.DataLoader`

Options
~~~~~~~

- :class:`~confab.options.Options`
- :func:`~confab.options.assume_yes`

Iterations
~~~~~~~~~~

- :func:`~confab.iter.iter_hosts_and_roles`
- :func:`~confab.iter.iter_conffiles`
- :func:`~confab.iter.make_conffiles`

Fabric Tasks
~~~~~~~~~~~~

- :func:`~confab.diff.diff`
- :func:`~confab.generate.generate`
- :func:`~confab.pull.pull`
- :func:`~confab.push.push`
