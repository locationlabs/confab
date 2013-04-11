Version 1.2

 -  Major refactor of underlying data model:
    -  `definitions.py` replaces `model.py` and `resolve.py`
    -  Provides a simpler object and iteration model for navigation confab settings.
    -  Moves host and role iteration out of `main.py` into `iterconffiles` function.
 -  No prevents multiple roles/components from defining the same template on the same host.
 -  Allows multiple loading of data from identically named files in different directories.
 -  Ensures that role data may override component data.
 -  Supports customized `module_as_dict` conversion.

Version 1.1

 -  Allows roles to have components: components may have templates
    and may be reused across different roles, with customization defined
    in role configuration data.
 -  Abstracts template and data loading into callable objects to allow ConfFiles
    to load templates and data for specific components.
 -  Allows data modules to be templates (`*.py_tmpl`) as well as Python files (`*.py`).
 -  Adds output verbosity control and more verbose output.
 -  Instead of enforcing that all hosts have the same role when invoking
    the `confab` CLI, "does the right thing."
 -  Changes uses of run() to sudo() and always uses `use_sudo` when calling put().
 -  Switches merge resolution order to respect environment configuration before role
    or component configuration.

