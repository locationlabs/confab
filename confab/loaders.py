"""
Jinja2 Environment loading helper functions.

Confab uses the environments list_templates() method to abstract
template location from rendering and synchronization.

Note that the default Jinja2 Loaders assume a charset (default: utf-8),
which means it will take special effort to handle binary data.
"""

from jinja2 import Environment, FileSystemLoader, PackageLoader, StrictUndefined
from os.path import join


class FileSystemEnvironmentLoader(object):
    """Loads Jinja2 environments from directories."""

    def __init__(self, dir_name):
        self.dir_name = dir_name

    def __call__(self, component):
        """
        Load a Jinja2 Environment for a component.
        """
        return Environment(loader=FileSystemLoader(join(self.dir_name, component)),
                           undefined=StrictUndefined)


class PackageEnvironmentLoader(object):
    """Loads Jinja2 environments from python packages."""

    def __init__(self, package_name, templates_path='templates'):
        self.package_name = package_name
        self.templates_path = templates_path

    def __call__(self, component):
        """
        Load a Jinja2 Environment for a component.
        """
        return Environment(loader=PackageLoader(self.package_name,
                                                package_path=join(self.templates_path, component)),
                           undefined=StrictUndefined)
