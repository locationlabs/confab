.. _templates:

Templates
=========

Confab uses Jinja2's environment to enumerate configuration
file templates. Any valid :class:`Jinja2 environment<jinja2.Environment>` may
be provided as long as it uses a Loader that supports
:meth:`jinja2.Environment.list_templates`. By default, Confab uses a
:class:`jinja2.FileSystemLoader`.

Templates are loaded from a directory tree based on the selected component(s).
For example, given the following directory structure::

    /path/to/base_dir/templates/foo/etc/motd.tail
    /path/to/base_dir/templates/foo/etc/hostname
    /path/to/base_dir/templates/bar/etc/cron.d/baz

If the ``foo`` component is selected, ``/etc/motd.tail`` and ``/etc/hostname``
will be loaded; if the ``bar`` component is selected, only ``/etc/cron.d/baz``
will be loaded. Note that configuration file names and paths may also be
templates.
