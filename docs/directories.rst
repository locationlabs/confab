.. _directories:

Directories
===========

Confab loads all of its definitions, generates :ref:`templates`, and saves
remote copies of configuration files in locations relative to a single base
directory.

A normal Confab directory tree might look like::

    base_dir/settings.py            # definitions
    base_dir/templates/{component}/ # templates for {component}
    base_dir/data/default.py        # default configuration data
    base_dir/data/{environment}.py  # per-environment configuration data
    base_dir/data/{role}.py         # per-role configuration data
    base_dir/data/{component}.py    # per-component configuration data
    base_dir/data/{host}.py         # per-host configuration data
    base_dir/generated/{hostname}/  # generated configuration files for hostname
    base_dir/remotes/{hostname}/    # copies of remote configuration files from hostname

Confab selects this base directory in one of several ways:

1.  By default, the base directory is the same directory where ``settings.py``
    was loaded.

    Both the ``confab`` console script and the
    :func:`~confab.autotasks.generate_tasks` function load ``settings.py`` and
    construct an :class:`~confab.definitions.EnvironmentDefinition`, which
    retains a reference to the directory where ``settings.py`` was loaded.
    This definition is saved in the Fabric environment as
    ``env.environmentdef`` for use by subsequent tasks.

2.  The :func:`~confab.diff.diff`, :func:`~confab.generate.generate`,
    :func:`~confab.pull.pull`, and :func:`~confab.push.push` tasks support an
    explicit directory argument.

3.  If all else fails, Confab falls back to ``os.getcwd()``.

