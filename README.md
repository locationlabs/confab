# Confab

Configuration management with Fabric and Jinja2.

## Overview

Confab provides four basic functions:

 1. It assumes a data model where *hosts* belong to one or more *environments*
    and are assigned to one or more *roles*.

 2. It defines a mechanism for loading configuration data based on a set of
    *defaults* and override values defined per *environment* or *host*.

 3. It defines a mechanism for loading Jinja2 templates for configuration files
    based on a *role*.

 4. It defines Fabric tasks to faciliate publishing configuration files generated
    from applying the configuration data to the Jinja2 templates to *hosts*.

It is suggested that Confab be used with configuration data and templates that
are checked in to version control so that publication is tied to versioning
and release process.

## Usage

Confab may be used in several ways:

 -  The distribution ships with the *confab* console script, which provides a 
    simple command line usage based on common defaults.

        confab -d /path/to/directory -H hosts -u user <command>

 -  Confab's tasks may be included in another fabfile simply by adding:
    
        from confab.api import *
    
    And then running:

        fab <task>:<arguments>

 -  Confab's lower level API can be invoked using customized data loading 
    functions, either to create new tasks or to be called directly from 
    a new console script.

        from confab.api import ConfFiles
        
        conffiles = ConfFiles(jinja2_environment,
                              data)


## Roles, Environments, and Hosts

Confab assumes the existings of hosts groupings that constitute different *environments* (e.g. production).
Likewise, confab assumes that each host has one or more *roles* that define how it is used. Within 
the default confab console script:

 -  Environment and host definitions are loaded from a **settings.py** file in the data directory, which
    should define the environment-to-host and role-to-host mappings as follows:

        environmentdefs = {
            'local': ['localhost']
        }
        
        roledefs = {
            'foo': ['localhost']
        }

 -  Templates are loaded from a directory tree based on role. That is, roles help specify which 
    configuration files to manage.

 -  Configuration data is loaded from python modules named after the environment or role names
    (or default), using the convention that the module's *__all__* value embodies its data:

        __all__ = {'foo': 'bar'}

    The dictionaries from these modules (if any) are recursively merged. (see below)

 -  Generated and remote configuration files will always be saved to a directory named after
    the fully qualified domain name (FQDN) of the target host.

Confab expects roles, environments, and definitions thereof to be saved in the Fabric environment,
though the lower level API should be tolerant to these values being absent. Confab likewise expects
the current host to be defined in Fabric's *env.host_string*; this requirement is absolute.


## Configuration Data

By default, Confab recursively merges configuration dictionaries from various sources,
using a three level hierarchy: 

 -  Default values are overridden by per-environment values
 -  Per-environment values are overridden by per-host values

Confab's recursive merge operation can be futher customized by using callable wrappers
around configuration values; confab will always delegate to a callable to define
how values are overriden, e.g. allowing lists values to be appended/prepended to
default values.


## Templates

Confab uses Jinja2's environment to enumerate configuration file templates. Any 
valid Jinja2 environment may be provided as long as it uses a Loader that supports
list_templates(). By default, Confab uses a FileSystemLoader.

Configuration file names and paths may also be templates.


## Tasks

Confab provides four default tasks:

 1. Generate configuration files from templates. (generate)

 2. Pull configuration files from a remote host. (pull)

 3. Show differences between generated and remote configuration files. (diff)

 4. Interactively push generated configuration files to a remote host. (push)


The default tasks all expect a series of directories as inputs:

 -  **templates_dir** is the root directory for loading templates.

 -  **data_dir** is the root directory for loading configuration data.

 -  **generated_dir** is the root directory where generated configuration files
    will be written.

 -  **remotes_dir** is the root directory where remote configuration files are
    saved.

When run from within a *fabfile*, these directories must be specified on the command line;
the *confab* console script assumes that all directories are defined relative to another
root directory specified on the command line.
