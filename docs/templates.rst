.. _templates:

Templates
=========

Confab uses Jinja2's environment to enumerate configuration file templates.
Any valid Jinja2 environment may be provided as long as it uses a Loader that
supports list_templates().  By default, Confab uses a FileSystemLoader.

Configuration file names and paths may also be templates.
