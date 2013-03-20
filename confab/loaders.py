"""
Jinja2 Environment loading helper functions.

Confab uses the environments list_templates() method to abstract
template location from rendering and synchronization.

Note that the default Jinja2 Loaders assume a charset (default: utf-8).
"""

from jinja2 import Environment, FileSystemLoader, PackageLoader, StrictUndefined, TemplateNotFound
from os import path


def load_environment_from_dir(dir_name):
    """
    Load a Jinja2 Environment from a directory name.
    """
    return Environment(loader=ConfabFileSystemLoader(dir_name, encoding='utf-8'),
                       undefined=StrictUndefined)


def load_environment_from_package(package_name):
    """
    Load a Jinja2 Environment from a package name.
    """
    return Environment(loader=PackageLoader(package_name, encoding='utf-8'),
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
            filename = path.join(searchpath, template)
            if path.exists(filename):
                return "", filename, True

        raise TemplateNotFound(template)
