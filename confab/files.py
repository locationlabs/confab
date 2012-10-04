"""
Abstractions related to finding and representing configuration files.
"""

from fabric.api import abort, env, get, put, puts, run, settings, sudo
from fabric.contrib.files import exists
from jinja2 import Environment, FileSystemLoader, PackageLoader, StrictUndefined

import os
import shutil

def env_from_dir(dir_name):
    """
    Create a Jinja2 Environment from a directory name.
    """
    return Environment(loader=FileSystemLoader(dir_name),
                       undefined=StrictUndefined)

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

def _clear_file(file_name):
    """
    Remove an entire directory tree.
    """
    if os.path.exists(file_name):
        os.remove(file_name)

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

    def _write_verbatim(self, generated_file_name):
        """
        Write the configuration file without templating.
        """
        shutil.copy2(self.template.filename, generated_file_name)

    def _write_template(self, generated_file_name):
        """
        Write the configuration file as a template.
        """
        with open(generated_file_name, 'w') as generated_file:
            generated_file.write(self.template.render(**self.data) + '\n')
            shutil.copystat(self.template.filename, generated_file_name)

    def generate(self, generated_file_name):
        """
        Write the configuration file to the dest_dir.
        """
        remote_file_name = os.sep + self.name

        puts('Generating {file_name}'.format(file_name=remote_file_name))

        # ensure that destination directory exists
        _ensure_dir(os.path.dirname(generated_file_name))

        if self.options.is_text(self.mime_type):
            self._write_template(generated_file_name)
        else:
            self._write_verbatim(generated_file_name)

    def pull(self, local_file_name):
        """
        Pull remote configuration file to local file.
        """
        remote_file_name = os.sep + self.name

        puts('Pulling {file_name} from {host}'.format(file_name=remote_file_name,
                                                      host=env.host_string))

        _ensure_dir(os.path.dirname(local_file_name))
        _clear_file(local_file_name)

        with settings(use_ssh_config = True):
            if exists(remote_file_name, use_sudo=self.options.use_sudo):
                get(remote_file_name, local_file_name)
            else:
                puts('Not found: {file_name}'.format(file_name=remote_file_name))


    def push(self, generated_file_name):
        """
        Push the generated configuration file to the remote host.
        """
        remote_file_name = os.sep + self.name
        remote_dir = os.path.dirname(remote_file_name)

        puts('Pushing {file_name} to {host}'.format(file_name=remote_file_name,
                                                    host=env.host_string))

        with settings(use_ssh_config = True):
            mkdir_cmd = sudo if self.options.use_sudo else run
            mkdir_cmd('mkdir -p {dir_name}'.format(dir_name=remote_dir))

            put(generated_file_name, 
                remote_file_name, 
                use_sudo=self.options.use_sudo, 
                mirror_local_mode=True)

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
                     
        
