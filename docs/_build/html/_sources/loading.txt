.. _loading:


Loading Roles, Environments, and Hosts
======================================

Within the :term:`confab` console script
----------------------------------------

Environment and host definitions are loaded from a **settings.py** file in the
main input directory.  This module should define the environment-to-host and
role-to-host mappings as follows::

    environmentdefs = {
        'local': ['localhost']
    }

    roledefs = {
        'foo': ['localhost']
    }

The **settings.py** file may also define a role-to-components mapping::

    componentdefs = {
        'foo': ['bar']
    }

If no component defs are defined or a role is absent from this mapping, the role
is assumed to be its own component.

Templates
---------

Templates are loaded from a directory tree based on component.

For example, in the following directory structure, the **foo** compoment manages
two configuration files and the **bar** component only one::

        /path/to/templates/foo/etc/motd.tail
        /path/to/templates/foo/etc/hostname
        /path/to/templates/bar/etc/cron.d/baz

