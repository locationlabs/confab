"""
Abstractions related to finding and representing configuration files.
"""

from confab.options import options

from fabric.api import abort, env, get, put, puts, run, settings, sudo
from fabric.colors import blue, red, green
from fabric.contrib.files import exists
from jinja2 import Environment, FileSystemLoader, PackageLoader, StrictUndefined

from difflib import unified_diff

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

    def __init__(self, template):
        self.template = template
        self.data = options.get_configuration_data()
        self.mime_type = options.get_mime_type(template.filename)
        self.name = template.environment.from_string(template.name).render(**self.data)
        self.remote = os.sep + self.name

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

    def diff(self, generated_dir, remotes_dir, output=False):
        """
        Compute whether there is a diff between the generated and local files.
        
        If output is enabled, show the diffs nicely.
        """
        generated_file_name = os.sep.join([generated_dir,env.host_string,self.name])
        local_file_name = os.sep.join([remotes_dir,env.host_string,self.name])
        remote_file_name = self.remote

        puts('Computing diff for {file_name}'.format(file_name=remote_file_name))

        if not os.path.exists(generated_file_name):
            if output:
                print(red('Only in remote: {file_name}'.format(file_name=remote_file_name)))
            return True

        if not os.path.exists(local_file_name):
            if output:
                print(blue(('Only in generated: {file_name}'.format(file_name=remote_file_name))))
            return True

        diff_lines = unified_diff(open(local_file_name).readlines(),
                                  open(generated_file_name).readlines(),
                                  fromfile='{file_name} (remote)'.format(file_name=remote_file_name),
                                  tofile='{file_name} (generated)'.format(file_name=remote_file_name))
        
        has_lines = False
        if output:
            for diff_line in diff_lines:
                if self.is_text() or self.is_empty():
                    color = red if diff_line.startswith('-') else blue if diff_line.startswith('+') else green
                    print(color(diff_line.strip()))
                    has_lines = True
                else:
                    print(green('Binary files differ: {file_name}'.format(file_name=remote_file_name)))
                    has_lines = True
                    break

        return has_lines

    def is_text(self):
        return options.is_text(self.mime_type)

    def is_empty(self):
        return options.is_empty(self.mime_type)

    def generate(self, generated_dir):
        """
        Write the configuration file to the dest_dir.
        """
        generated_file_name = os.sep.join([generated_dir,env.host_string,self.name])
        remote_file_name = self.remote

        puts('Generating {file_name}'.format(file_name=remote_file_name))

        # ensure that destination directory exists
        _ensure_dir(os.path.dirname(generated_file_name))

        if self.is_text():
            self._write_template(generated_file_name)
        else:
            self._write_verbatim(generated_file_name)

    def pull(self, remotes_dir):
        """
        Pull remote configuration file to local file.
        """
        local_file_name = os.sep.join([remotes_dir,env.host_string,self.name])
        remote_file_name = self.remote

        puts('Pulling {file_name} from {host}'.format(file_name=remote_file_name,
                                                      host=env.host_string))

        _ensure_dir(os.path.dirname(local_file_name))
        _clear_file(local_file_name)

        with settings(use_ssh_config = True):
            if exists(remote_file_name, use_sudo=options.use_sudo):
                get(remote_file_name, local_file_name)
            else:
                puts('Not found: {file_name}'.format(file_name=remote_file_name))


    def push(self, generated_dir):
        """
        Push the generated configuration file to the remote host.
        """
        generated_file_name = os.sep.join([generated_dir,env.host_string,self.name])
        remote_file_name = self.remote
        remote_dir = os.path.dirname(remote_file_name)

        puts('Pushing {file_name} to {host}'.format(file_name=remote_file_name,
                                                    host=env.host_string))

        with settings(use_ssh_config = True):
            mkdir_cmd = sudo if options.use_sudo else run
            mkdir_cmd('mkdir -p {dir_name}'.format(dir_name=remote_dir))

            put(generated_file_name, 
                remote_file_name, 
                use_sudo=options.use_sudo, 
                mirror_local_mode=True)

class _BinaryTemplate(object):
    """
    Unfortunate workaround for Jinja2 Environment assuming templates use a
    text encoding. Simply substitutes a duck-typed template for a Jinja
    one. Necessary as long as we want to use the Environment's list_templates()
    to enumerate configuration files and want to allow binary files.
    
    Currently only works with FileSystemLoader.
    """
    
    def __init__(self, name, environment):
        self.name = name
        self.environment = environment

        for path in environment.loader.searchpath:
            filename = os.sep.join([path, name])
            if os.path.exists(filename):
                self.filename = filename
                break

    def render(self, **kwargs):
        return open(self.filename).read()

def get_conf_files(environment):
    """
    Generate a list of configuration files using a Jinja2 Environment
    and an optional filter function.

    The Environment must use a Loader that supports list_templates().
    """

    def get_template(template_name):
        try:
            return environment.get_template(template_name)
        except UnicodeDecodeError:
            return _BinaryTemplate(template_name, environment)

    def conf_file(template_name):
        return ConfFile(get_template(template_name)
)

    return map(conf_file,environment.list_templates(filter_func=options.filter_func))
                     
        
