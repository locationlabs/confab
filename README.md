# Confab

Configuration management with Fabric and Jinja2.

## Quickstart

 1. Install confab:

        pip install confab

 2. Create a `settings.py` file:
 
        cat > settings.py << "EOF"
        environmentdefs = {
            'local': ['localhost']
        }
        
        roledefs = {
            'example': ['localhost']
        }
        EOF
   
 3. Create a template:

        mkdir -p templates/example/tmp/
        echo '{{ value }}' > templates/example/tmp/hello.txt

 4. Create data to populate the template:

        mkdir -p data
        echo 'value = "world"' > data/default.py

 5. Review the difference between the template value and the value on the target host:
 
        confab diff
    
 6. Push changes to the target host:
 
        confab push

 7. Review the change:

        ssh localhost cat /tmp/hello.txt

## Overview

Confab provides four basic functions:

 1. It defines a data model where *hosts* belong to one or more *environments*
    and are assigned to one or more *roles*, which can be made up of *components*.

 2. It defines a mechanism for loading configuration data based on a set of
    *defaults* and override values defined per *environment*, *host*, *role*,
    or *component*.

 3. It defines a mechanism for loading Jinja2 templates for configuration files
    based on a *role* and/or *component*.

 4. It defines Fabric tasks to faciliate publishing configuration files generated
    from applying the configuration data to the Jinja2 templates to *hosts*.

Confab's configuration data and templates are expected to be checked in to version control
so that changes to configuration are managed through a regular versioning and release process.

## Tasks

Confab provides four default tasks:

 1. Generate configuration files from templates. (`generate`)

 2. Pull copies of configuration files from a remote host. (`pull`)

 3. Show differences between generated and remote configuration files. (`diff`)

 4. Interactively push generated configuration files to a remote host. (`push`)

## Definitions

By default, Confab reads its definition from a series of mappings in a `settings.py` file.

 -  *hosts*, which are physical or virtual machines accessible via ssh, are mapped to 
    *environments*, which are groups of hosts that work together for a single purpose,
    using an `environmentdefs` declaration:
    
        environmentdefs = {
            'local': ['localhost'],
        }
    
    The default *environment* is assumed to be called `local`, but it's common to have one
    environment for development, one for staging, one for production, and so forth.

 -  *roles*, which define specific purposes for hosts, are mapped to hosts using a 
    `roledefs` declaration:
    
        roledefs = {
            'role1': ['localhost'],
        }
 
 -  *components*, which define slices of configuration files, are mapped to roles and/or
    other components using a `componentdefs` mapping:
    
        componentdefs = {
            'role': ['component1', 'group1'],
            'group1': ['component2', 'component3'],
        }

    The configuration files that Confab manages are controlled by which components are selected.
    In the degenerate case where a role has no components, the role itself is taken to be a
    component and configuration files are selected based on the role's name.

## Usage

Confab may be used in several ways:

 -  The distribution ships with the *confab* console script, which provides a 
    simple command line usage pattern:

        confab -d /path/to/base_dir -H hosts -u user <command>

 -  Confab's tasks may be included in another fabfile simply by adding:
    
        from confab.api import diff, generate, generate_tasks, pull, push

        # generate environment tasks
        generate_tasks('/path/to/settings')
    
    And then running:

        fab <env_name>:{role1},{role2} <task>:<arguments>

    Note that the settings path and roles list are optional.

 -  Confab's lower level API can be invoked directly either to create new tasks
    or as part of some other script:

        from confab.api import ConfFiles, Settings
        
        settings = Settings.load_from_module(settings_path)
        
        for host_and_role in settings.for_env(env_name).iterall():
            conffiles = ConfFiles(host_and_role,
                                  environment_loader,
                                  data_loader)

## Directories

Confab loads all of its definitions, generates templates, and save remote copies
of configuration files in locations relative to a single base directory.

A normal Confab directory tree might look like:

    /path/to/base_dir/settings.py            # definitions
    /path/to/base_dir/templates/{component}/ # templates for {component}
    /path/to/base_dir/data/default.py        # default configuration data
    /path/to/base_dir/data/{environment}.py  # per-environment configuration data
    /path/to/base_dir/data/{role}.py         # per-role configuration data
    /path/to/base_dir/data/{component}.py    # per-component configuration data
    /path/to/base_dir/data/{host}.py         # per-host configuration data
    /path/to/base_dir/generated/{hostname}/  # generated configuration files for hostname
    /path/to/base_dir/remotes/{hostname}/    # copies of remote configuration files from hostname

Confab selects this base directory in one of several ways:

 1. By default, the base directory is the same directory where `settings.py` was loaded.

    Both the `confab` console script and the `generate_tasks` function load `settings.py`
    and construct an `EnvironmentDefinition`, which retains a reference to the directory
    where `settings.py` was loaded. This definition is saved in the Fabric environment as
    `env.environmentdef` for use by subsequent tasks.
    
 2. The `diff`, `generate`, `pull`, and `push` tasks support an explicit directory argument.
 
 3. If all else fails, Confab falls back to `os.getcwd()`.

## Templates

Templates are loaded from a directory tree based on the selected component(s). For example,
given the following directory structure:

    /path/to/base_dir/templates/foo/etc/motd.tail
    /path/to/base_dir/templates/foo/etc/hostname
    /path/to/base_dir/templates/bar/etc/cron.d/baz

If the `foo` component is selected, `/etc/motd.tail` and `/etc/hostname` will be loaded; if
the `bar` component is selected, only `/etc/cron.d/baz` will be loaded. Note that
configuration file names and paths may also be templates.

## Data Loading

Configuration data is loaded from python modules named after the selected environment, role,
component, and host, plus a standard set of defaults. For example, if Confab is operating
on an environment named "foo", a role named "bar", a component named "baz", and a host named "host",
configuration data would be loaded for `foo.py`, `bar.py`, `baz.py`, `host.py`, 
and `default.py`.

If a configuration data module is not found, Confab will also look for a file with a `.py_tmpl`
suffix and treat it as a Jinja2 template for the same module, allowing configuration data to
use Jinja2 template syntax (including "include").

Confab uses the *__dict__* property of the loaded module to generate dictionary, filtering out
any entries starting with '_'. In other words, this module:

    foo = 'bar'
    _ignore = 'this'
		
results in this dictionary:
	
	{'foo': 'bar'}

## Merging

The dictionaries from all of the loaded modules (if any) are recursively merged into a
single dictionary, which is then used to populate templates. Merging operates in the
following order:
    
 -  Host-specific values are used first.
 -  Environment-specific values are used next. 
 -  Role-specific values are used next.
 -  Component default values are used next.
 -  Default values are used last.

Confab's recursive merge operation can be futher customized by using callable wrappers
around configuration values; Confab will always delegate to a callable to define
how values are overriden, e.g. allowing lists values to be appended/prepended to
default values.
