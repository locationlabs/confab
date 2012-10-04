"""
Abstractions related to finding and representing configuration files.
"""

from jinja2 import Environment, PackageLoader, StrictUndefined

import os
import shutil

def env_from_package(package_name):
    """
    Create a Jinja2 Environment from a package name.
    """
    return Environment(loader=PackageLoader(package_name),
                       undefined=StrictUndefined)

def _clear_dir(dir_name):
    """
    Remove an entire directory tree.
    """
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)

def _ensure_dir(dir_name):
    """
    Ensure that a directory exists.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

class ConfFile(object):
    """
    Representation of a configuration file.
    """

    def __init__(self, template, data, options):
        self.template = template
        self.data = data
        self.options = options
        self.mime_type = options.get_mime_type(template.filename)
        self.name = template.environment.from_string(template.name).render(**data)

    def _write_verbatim(self, dest_file_name):
        """
        Write the configuration file to the dest_dir verbatim, without templating.
        """
        shutil.copy2(self.template.filename, dest_file_name)

    def _write_template(self, dest_file_name):
        """
        Write the configuration file to the dest_dir as a template.
        """
        with open(dest_file_name, 'w') as dest_file:
            dest_file.write(self.template.render(**self.data) + '\n')
            shutil.copystat(self.template.filename, dest_file_name)

    def write(self, dest_file_name):
        """
        Write the configuration file to the dest_dir.
        """

        # ensure that destination directory exists
        _ensure_dir(os.path.dirname(dest_file_name))

        if self.options.is_text(self.mime_type):
            self._write_template(dest_file_name)
        else:
            self._write_verbatim(dest_file_name)


def get_conf_files(env, data, options):
    """
    Generate a list of configuration files using a Jinja2 Environment
    and an optional filter function.

    The Environment must use a Loader that supports list_templates().
    """

    def conf_file(template_name):
        return ConfFile(env.get_template(template_name),
                        data,
                        options)

    return map(conf_file,env.list_templates(filter_func=options.filter_func))
                     
        
