"""
Configuration file template object model.
"""

from confab.files import _clear_dir, _clear_file, _ensure_dir
from confab.options import options

from fabric.api import get, put, puts, run, settings, sudo
from fabric.colors import blue, red, green, magenta
from fabric.contrib.files import exists
from fabric.contrib.console import confirm
from difflib import unified_diff

import os
import shutil

class ConfFile(object):
    """
    Encapsulation of a configuration file template.
    """

    def __init__(self, template, data):
        self.template = template
        self.data = data
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
        generated_file_name = os.sep.join([generated_dir,self.name])
        local_file_name = os.sep.join([remotes_dir,self.name])
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
                if self.should_render() or self.is_empty():
                    color = red if diff_line.startswith('-') else blue if diff_line.startswith('+') else green
                    print(color(diff_line.strip()))
                    has_lines = True
                else:
                    print(green('Binary files differ: {file_name}'.format(file_name=remote_file_name)))
                    has_lines = True
                    break

        return has_lines

    def should_render(self):
        return options.should_render(self.mime_type)

    def is_empty(self):
        return options.is_empty(self.mime_type)

    def generate(self, generated_dir):
        """
        Write the configuration file to the dest_dir.
        """
        generated_file_name = os.sep.join([generated_dir,self.name])
        remote_file_name = self.remote

        puts('Generating {file_name}'.format(file_name=remote_file_name))

        # ensure that destination directory exists
        _ensure_dir(os.path.dirname(generated_file_name))

        if self.should_render():
            self._write_template(generated_file_name)
        else:
            self._write_verbatim(generated_file_name)

    def pull(self, remotes_dir):
        """
        Pull remote configuration file to local file.
        """
        local_file_name = os.sep.join([remotes_dir,self.name])
        remote_file_name = self.remote

        puts('Pulling {file_name} from {host}'.format(file_name=remote_file_name,
                                                      host=options.get_hostname()))

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
        generated_file_name = os.sep.join([generated_dir,self.name])
        remote_file_name = self.remote
        remote_dir = os.path.dirname(remote_file_name)

        puts('Pushing {file_name} to {host}'.format(file_name=remote_file_name,
                                                    host=options.get_hostname()))

        with settings(use_ssh_config = True):
            mkdir_cmd = sudo if options.use_sudo else run
            mkdir_cmd('mkdir -p {dir_name}'.format(dir_name=remote_dir))

            put(generated_file_name, 
                remote_file_name, 
                use_sudo=options.use_sudo, 
                mirror_local_mode=True)

class ConfFiles(object):
    """
    Encapsulation of a set of configuration files.
    """
    
    def __init__(self,
                 environment,
                 data):
        """
        On init, load a list of configuration files using the provide Jinja2 Environment
        and an optional filter function.

        The Environment must use a Loader that supports list_templates().
        """
        self.environment = environment
        self.data = data

        self.conffiles = map(lambda template_name: ConfFile(environment.get_template(template_name), data),
                             environment.list_templates(filter_func=options.filter_func))

    def generate(self, generated_dir):
        """
        Write all configuration files to generated_dir.
        """
        host_generated_dir = os.sep.join([generated_dir,options.get_hostname()])

        _clear_dir(host_generated_dir)
        _ensure_dir(host_generated_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

    def pull(self, remotes_dir):
        """
        Pull remote versions of files into remotes_dir.
        """
        host_remotes_dir = os.sep.join([remotes_dir,options.get_hostname()])

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)
        
    def diff(self, generated_dir, remotes_dir):
        """
        Show diffs for all configuration files.
        """
        host_generated_dir = os.sep.join([generated_dir,options.get_hostname()])
        host_remotes_dir = os.sep.join([remotes_dir,options.get_hostname()])

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

        for conffile in self.conffiles:
            conffile.diff(host_generated_dir, host_remotes_dir, True)
        
    def push(self, generated_dir, remotes_dir):
        """
        Push configuration files that have changes, given user confirmation.
        """
        host_generated_dir = os.sep.join([generated_dir,options.get_hostname()])
        host_remotes_dir = os.sep.join([remotes_dir,options.get_hostname()])

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

        has_diff = lambda conffile: conffile.diff(host_generated_dir, host_remotes_dir, True)
        with_diffs = filter(has_diff, self.conffiles)

        if not with_diffs:
            print(magenta('No configuration files to push for {host}'.format(host=options.get_hostname())))
            return

        print(magenta('The following configuration files have changed for {host}:'.format(host=options.get_hostname())))
        print
        for conffile in with_diffs:
            print(magenta('\t' + conffile.remote))

        if confirm('Push configuration files to {host}?'.format(host=options.get_hostname()),
                   default=False):
            for conffile in with_diffs:
                conffile.push(host_generated_dir)
