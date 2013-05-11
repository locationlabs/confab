.. _api_module:

:mod:`confab.api`
-----------------

.. module:: confab.api

Core
~~~~

- :class:`confab.conffiles.ConfFiles`

Model Loading
~~~~~~~~~~~~~

- :func:`confab.model.load_model_from_dir`
- :func:`confab.model.load_model_from_dict`

Jinja2 Environment Loading
~~~~~~~~~~~~~~~~~~~~~~~~~~

- :class:`~confab.loaders.FileSystemEnvironmentLoader`
- :class:`~confab.loaders.PackageEnvironmentLoader`

Data Loading
~~~~~~~~~~~~

- :class:`~confab.dataDataLoader`

Options
~~~~~~~

- :class:`~confab.options.Options`
- :func:`~confab.options.assume_yes`

Fabric Tasks
~~~~~~~~~~~~

- :func:`~confab.diff.diff`
- :func:`~confab.generate.generate`
- :func:`~confab.pull.pull`
- :func:`~confab.push.push`
