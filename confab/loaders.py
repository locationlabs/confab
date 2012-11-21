"""
Jinja2 Environment loading helper functions.

Confab uses the environments list_templates() method to abstract
template location from rendering and synchronization.

Note that the default Jinja2 Loaders assume a charset (default: utf-8),
which means it will take special effort to handle binary data.
"""

from jinja2 import Environment, FileSystemLoader, PackageLoader, StrictUndefined


def load_environment_from_dir(dir_name):
    """
    Load a Jinja2 Environment from a directory name.
    """
    return Environment(loader=FileSystemLoader(dir_name),
                       undefined=StrictUndefined)


def load_environment_from_package(package_name):
    """
    Load a Jinja2 Environment from a package name.
    """
    return Environment(loader=PackageLoader(package_name),
                       undefined=StrictUndefined)
