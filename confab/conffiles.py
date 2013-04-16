"""
Configuration file template object model.
"""
from os.path import dirname, exists, join
from hashlib import sha1
from warnings import warn
from fabric.api import get, put, sudo
from fabric.colors import blue, red, green, magenta
from fabric.contrib.files import exists as exists_remote
from fabric.contrib.console import confirm
from gusset.output import debug, status

from confab.files import _clear_dir, _clear_file, _ensure_dir
from confab.options import options
from confab.validate import assert_may_be_created

import os
import shutil


class ConfFileDiff(object):
    """
    Encapsulation of the differences between the (locally copied) remote and
    generated versions of a configuration file.
    """

    def __init__(self, remote_file_name, generated_file_name, conffile_name):
        """
        Compute whether the conffile with the given name has changed given
        a remote and generate file copy.
        """
        self.missing_generated = False
        self.missing_remote = False
        self.conffile_name = conffile_name
        self.diff_lines = []

        if not exists(generated_file_name):
            self.missing_generated = True

        if not exists(remote_file_name):
            self.missing_remote = True

        if not self.missing_generated and not self.missing_remote:
            diff_iter = options.diff(open(remote_file_name).readlines(),
                                     open(generated_file_name).readlines(),
                                     fromfile='{file_name} (remote)'.format(file_name=conffile_name),
                                     tofile='{file_name} (generated)'.format(file_name=conffile_name))

            # unified_diff returns a generator
            self.diff_lines = list(diff_iter)

    def show(self):
        """
        Print the diff using pretty colors.

        If confab is used on binary files, diffs are likely to render poorly.
        """
        if self.missing_generated:
            if not self.missing_remote:
                print(red('Only in remote: {file_name}'.format(file_name=self.conffile_name)))
        elif self.missing_remote:
            print(blue(('Only in generated: {file_name}'.format(file_name=self.conffile_name))))
        else:
            for diff_line in self.diff_lines:
                color = red if diff_line.startswith('-') else blue if diff_line.startswith('+') else green
                print(color(diff_line.strip()))

    def __nonzero__(self):
        """
        Evaluate to true if there is a diff.
        """
        if self.missing_generated:
            return not self.missing_remote
        elif self.missing_remote:
            return True
        else:
            return len(self.diff_lines)


class ConfFile(object):
    """
    Encapsulation of a configuration file template.
    """

    def __init__(self, template, data, component):
        self.template = template
        self.data = data
        self.host = component.host
        self.role = component.role
        self.component = component.name
        self.environment = component.environment
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
            rendered = self.template.render(**self.data).encode('utf-8')
            generated_file.write(rendered)
            generated_file.write(u'\n')
            shutil.copystat(self.template.filename, generated_file_name)

    def diff(self, generated_dir, remotes_dir, output=False):
        """
        Compute the diff between the generated and remote files.

        If output is enabled, show the diffs nicely.
        """
        generated_file_name = join(generated_dir, self.name)
        assert_may_be_created(generated_file_name)

        remote_file_name = join(remotes_dir, self.name)
        assert_may_be_created(remote_file_name)

        status('Computing diff for {file_name}', file_name=self.remote)

        return ConfFileDiff(remote_file_name, generated_file_name, self.remote)

    def should_render(self):
        return options.should_render(self.mime_type)

    def is_empty(self):
        return options.is_empty(self.mime_type)

    def hexdigest(self):
        """
        Return a hex digest of conffile content.
        """
        if self.should_render():
            content = self.template.render(**self.data).encode('utf-8')
        else:
            with open(self.template.filename) as file_:
                content = file_.read()
        return sha1(content).hexdigest()

    def generate(self, directory):
        """
        Write the configuration file.
        """
        generated_file_name = join(directory, self.name)
        assert_may_be_created(generated_file_name)

        status('Generating {file_name}', file_name=self.remote)

        # ensure that destination directory exists
        _ensure_dir(directory)

        if self.should_render():
            self._write_template(generated_file_name)
        else:
            self._write_verbatim(generated_file_name)

    def pull(self, directory):
        """
        Pull remote configuration file to local file.
        """
        local_file_name = join(directory, self.name)
        assert_may_be_created(local_file_name)

        status('Pulling {file_name} from {host}',
               file_name=self.remote,
               host=self.host)

        _ensure_dir(directory)
        _clear_file(local_file_name)

        if exists_remote(self.remote, use_sudo=True):
            get(self.remote, local_file_name)
        else:
            status('Not found: {file_name}',
                   file_name=self.remote)

    def push(self, directory):
        """
        Push the generated configuration file to the remote host.
        """
        generated_file_name = join(directory, self.name)
        assert_may_be_created(generated_file_name)
        remote_dir = dirname(self.remote)

        status('Pushing {file_name} to {host}',
               file_name=self.remote,
               host=self.host)

        sudo('mkdir -p {dir_name}'.format(dir_name=remote_dir))

        put(generated_file_name,
            self.remote,
            use_sudo=True,
            mirror_local_mode=True)


class ConfFiles(object):
    """
    Encapsulation of a set of configuration files.
    """

    def __init__(self,
                 host_and_role,
                 environment_loader,
                 data_loader):
        """
        A set of templated configuration files.

        :param host_and_role: An instance of HostAndRoleDefinition
        :param environment_loader: An environment loader (e.g. FileSystemEnvironmentLoader)
        :param data_load: An instance DataLoader

        The environment loader must return a Jinja2 environment with an underlying
        loader that supports list_templates(). On init, ConfFiles will load all
        templates in the environment for the specified host and role (including any
        role components).

        The environment loader must return a Jinja2 environment that uses a
        loader that supports list_templates().
        """
        self.conffiles = []
        self.host = host_and_role.host
        self.role = host_and_role.role
        self.environment = host_and_role.environment

        # default base path for generated and remotes directories
        self.directory = host_and_role.environmentdef.directory or os.getcwd()

        for component in host_and_role.components():
            debug("Processing: {}".format(component.name))

            data = data_loader(component)
            environment = environment_loader(component.name)

            for template_name in environment.list_templates(filter_func=options.filter_func):
                debug("Adding template: {}".format(template_name))

                self.conffiles.append(ConfFile(environment.get_template(template_name),
                                               data,
                                               component))

        if not self.conffiles:
            warn("No conffiles found for '{role}' on '{host}' in environment '{environment}'"
                 .format(role=self.role,
                         host=self.host,
                         environment=self.environment))

    def _get_host_generated_dir(self, directory):
        return join(directory or self.directory,
                    options.get_generated_dir(),
                    self.host)

    def _get_host_remotes_dir(self, directory):
        return join(directory or self.directory,
                    options.get_remotes_dir(),
                    self.host)

    def generate(self, directory=None):
        """
        Write all configuration files to generated_dir.
        """
        host_generated_dir = self._get_host_generated_dir(directory)

        _clear_dir(host_generated_dir)
        _ensure_dir(host_generated_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

    def pull(self, directory=None):
        """
        Pull remote versions of files into remotes_dir.
        """
        host_remotes_dir = self._get_host_remotes_dir(directory)

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)

    def diff(self, directory=None):
        """
        Show diffs for all configuration files.
        """
        host_generated_dir = self._get_host_generated_dir(directory)
        host_remotes_dir = self._get_host_remotes_dir(directory)

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

        for conffile in self.conffiles:
            conffile.diff(host_generated_dir, host_remotes_dir).show()

    def push(self, directory=None):
        """
        Push configuration files that have changes, given user confirmation.
        """
        host_generated_dir = self._get_host_generated_dir(directory)
        host_remotes_dir = self._get_host_remotes_dir(directory)

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

        has_diff = lambda conffile: conffile.diff(host_generated_dir, host_remotes_dir, True)
        with_diffs = filter(has_diff, self.conffiles)

        if not with_diffs:
            print(magenta('No configuration files to push for {host}'
                          .format(host=self.host)))
            return

        print(magenta('The following configuration files have changed for {host}:'
                      .format(host=self.host)))
        print
        for conffile in with_diffs:
            print(magenta('\t' + conffile.remote))

        if options.assume_yes or confirm('Push configuration files to {host}?'
                                         .format(host=self.host),
                                         default=False):
            for conffile in with_diffs:
                conffile.push(host_generated_dir)
