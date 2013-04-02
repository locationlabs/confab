# Confab

Configuration management with Fabric and Jinja2.


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

It is suggested that Confab be used with configuration data and templates that
are checked in to version control so that publication is tied to the versioning
and release process.


## Definitions

 -  *hosts* are physical or virtual machines accessible via ssh; Confab will normally 
    identify hosts by their fully qualified domain name (FQDN), so hostnames matter.

 -  *environments* are groups of hosts that work together for a single purpose; it's
    common to have one environment for development, one for staging, one for production
	and so forth.

 -  *components* are slices of configuration files; the configuration files that Confab 
    manages are controlled by which components are selected.

 -  *roles* are groups of zero or more components that achieve a common purpose; in the
    degenerate case where a role has no components, the role itself is taken to be
    a component.

## Usage

Confab may be used in several ways:

 -  The distribution ships with the *confab* console script, which provides a 
    simple command line usage based on common defaults.

        confab -d /path/to/directory -H hosts -u user <command>

    Confab then loads its definitions, configuration data, and templates
    from within the provided directory as follows:

        /path/to/directory/settings.py            # definitions
        /path/to/directory/templates/{component}/ # templates for {component}
        /path/to/directory/data/default.py        # default configuration data
        /path/to/directory/data/{environment}.py  # per-environment configuration data
        /path/to/directory/data/{role}.py         # per-role configuration data
        /path/to/directory/data/{component}.py    # per-component configuration data
        /path/to/directory/data/{host}.py         # per-host configuration data
        /path/to/directory/generated/{hostname}/  # generated configuration files for hostname
        /path/to/directory/remotes/{hostname}/    # copies of remote configuration files from hostname

 -  Confab's tasks may be included in another fabfile simply by adding:
    
        from confab.api import *
    
    And then running:

        fab <task>:<arguments>

    When invoking Confab tasks from *fab*, configuration directories must be provided
    as task arguments.
    
    To specify *roles* and *environments* to customize configuration data, the fabfile
    can use the *autotasks*, for example:

        from confab.api import *
        from confab.autotasks import autogenerate_tasks
        
        # load roledefs and environmentdefs from settings.py
        load_model_from_dir('/path/to/directory')
        # create tasks for each defined role and environment
        autogenerate_tasks()

    Autotasks would then allow fab to run as:

        fab role_{role} env_{environment} <task>:arguments

 -  Confab's lower level API can be invoked using customized data loading 
    functions, either to create new tasks or to be called directly from 
    a new console script.

        from confab.api import ConfFiles
        
        conffiles = ConfFiles(jinja2_environment_loader,
                              data_loader)


## Loading Roles, Environments, and Hosts

Within the default *confab* console script:

 -  Environment and host definitions are loaded from a **settings.py** file in the main input
    directory. This module should define the environment-to-host and role-to-host mappings as follows:

        environmentdefs = {
            'local': ['localhost']
        }
        
        roledefs = {
            'foo': ['localhost']
        }

 -  The **settings.py** file may also define a role-to-components mapping:

        componentdefs = {
            'foo': ['bar']
        }

    If no component defs are defined or a role is absent from this mapping, the role is assumed
    to be its own component.

 -  Templates are loaded from a directory tree based on component. For example, in the following 
    directory structure, the **foo** compoment manages two configuration files and the **bar** 
	component only one:

        /path/to/templates/foo/etc/motd.tail
        /path/to/templates/foo/etc/hostname
        /path/to/templates/bar/etc/cron.d/baz

 -  Configuration data is loaded from python modules named after the names of the selected
    environment, role, component, and host, plus a standard set of defaults. The dictionaries
    from these modules (if any) are recursively merged (see below), so that given an environment
    named "foo", a role named "bar", a component named "baz", and a host named "host", the
    configuration data would be merged between **default.py**, **foo.py**, **bar.py**, **baz.py**,
    and **host.py**.
    
    Confab uses the *__dict__* property of the loaded module, but filters out any entries 
	starting with '_'. In other words, this module:

        foo = 'bar'
		_ignore = 'this'
		
	results in this dictionary:
	
	    {'foo': 'bar'}
        
 -  If a configuration data module is not found, Confab will also look for a file with a `.py_tmpl`
    suffix and treat it as a Jinja2 template for the same module, allowing configuration data to
    use Jinja2 template syntax (including includes).

Confab expects roles, environments, and definitions thereof to be saved in the Fabric environment. 
The *confab* console script requires these definitions, although the lower level API is designed
to be tolerant of these values being absent. Both the console script and the lower level API
require that the current host be defined in Fabric's *env.host_string*.


## Configuration Data

By default, Confab recursively merges configuration dictionaries from various sources,
using a three level hierarchy: 

 -  Host-specific values are used first.
 -  Environment-specific values are used next. 
 -  Role or component-specific values are used next.
 -  Default values are used last.

Confab's recursive merge operation can be futher customized by using callable wrappers
around configuration values; Confab will always delegate to a callable to define
how values are overriden, e.g. allowing lists values to be appended/prepended to
default values.


## Templates

Confab uses Jinja2's environment to enumerate configuration file templates. Any 
valid Jinja2 environment may be provided as long as it uses a Loader that supports
list\_templates(). By default, Confab uses a FileSystemLoader.

Configuration file names and paths may also be templates.


## Tasks

Confab provides four default tasks:

 1. Generate configuration files from templates. (**generate**)

 2. Pull configuration files from a remote host. (**pull**)

 3. Show differences between generated and remote configuration files. (**diff**)

 4. Interactively push generated configuration files to a remote host. (**push**)


The default tasks all expect a series of directories as inputs:

 -  **templates_dir** is the root directory for loading templates.

 -  **data_dir** is the root directory for loading configuration data.

 -  **generated_dir** is the root directory where generated configuration files
    will be written.

 -  **remotes\_dir** is the root directory where remote configuration files are
    saved.

When run from within a *fabfile*, these directories must be specified on the command line;
the *confab* console script assumes that all directories are defined relative to another
root directory specified on the command line.


## Future Work

1. Confab needs a better **push** command line interface, and the following is a possible 
   option. 

```
The following configuration files have changed for localhost:

   no  |    filename                                              |  changed
       |                                                          |
   1   |    /etc/iptables.rules                                   |  new
   2   |    /etc/iptables.rules.services                          |  yes
   3   |    /opt/wm/etc/sprint_sms_gateway/gateway.properties     |  no

Select files to push? [all/None/..1,2..] 1,3
```

2. Similarly **diff** should offer a similar option to select files to show diffs.

```
The following configuration files have changed for localhost:

   no  |    filename                                              |  changed
       |                                                          |
   1   |    /etc/iptables.rules                                   |  new
   2   |    /etc/iptables.rules.services                          |  yes
   3   |    /opt/wm/etc/sprint_sms_gateway/gateway.properties     |  no

See changes for file(s)? [all/..1,2..] 1,3
```
