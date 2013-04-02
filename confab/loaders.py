"""
Jinja2 Environment loading helper functions.

Confab uses the environments list_templates() method to abstract
template location from rendering and synchronization.

Note that the default Jinja2 Loaders assume a charset (default: utf-8).
"""

from jinja2 import (Environment, FileSystemLoader, PackageLoader, BaseLoader,
                    StrictUndefined, TemplateNotFound)
from os.path import join, exists
from pkg_resources import get_provider


class FileSystemEnvironmentLoader(object):
    """Loads Jinja2 environments from directories."""

    def __init__(self, dir_name):
        self.dir_name = dir_name

    def __call__(self, component):
        """
        Load a Jinja2 Environment for a component.
        """
        component_path = join(self.dir_name, component)

        if not exists(component_path):
            return Environment(loader=EmptyLoader())

        return Environment(loader=ConfabFileSystemLoader(component_path),
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
        package_path = join(self.templates_path, component)

        provider = get_provider(self.package_name)
        if not provider.resource_isdir(package_path):
            return Environment(loader=EmptyLoader())

        return Environment(loader=PackageLoader(self.package_name, package_path),
                           undefined=StrictUndefined)


class ConfabFileSystemLoader(FileSystemLoader):
    """Adds support for binary templates when loading an environment from the file system.

    Binary config files cannot be loaded as Jinja templates by default, but since confab's
    model is built around Jinja environments we need to make sure we can still represent
    them as jinja Templates.

    Since confab only renders templates from text config files (see
    :py:meth:`confab.conffiles.Conffile.generate` and :py:meth:`confab.options.should_render`)
    we can workaround this by returning a dummy template for binary config files
    with the appropriate metadata. When generating the configuration, confab,
    instead of rendering the template, will just copy the template file
    (the binary config file) verbatim to the generated folder.
    """

    def get_source(self, environment, template):

        try:
            return super(ConfabFileSystemLoader, self).get_source(environment, template)
        except UnicodeDecodeError:
            pass  # not a text file

        for searchpath in self.searchpath:
            filename = join(searchpath, template)
            if exists(filename):
                return "", filename, True

        raise TemplateNotFound(template)


class EmptyLoader(BaseLoader):
    """Jinja template loader with no templates."""

    def list_templates(self):
        return []
