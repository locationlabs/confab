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

