"""
Configuration file template object model.
"""

from confab.files import _clear_dir, _clear_file, _ensure_dir
from confab.options import options

from fabric.api import get, put, puts, run, settings, sudo
from fabric.colors import blue, red, green, magenta
from fabric.contrib.files import exists
from fabric.contrib.console import confirm

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

        if not os.path.exists(generated_file_name):
            # Unexpected
            self.missing_generated = True

        if not os.path.exists(remote_file_name):
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
            # Unexpected
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
        Compute the diff between the generated and remote files.

        If output is enabled, show the diffs nicely.
        """
        generated_file_name = os.sep.join([generated_dir, self.name])
        remote_file_name = os.sep.join([remotes_dir,self .name])

        puts('Computing diff for {file_name}'.format(file_name=self.remote))

        return ConfFileDiff(remote_file_name, generated_file_name, self.remote)

    def should_render(self):
        return options.should_render(self.mime_type)

    def is_empty(self):
        return options.is_empty(self.mime_type)

    def generate(self, generated_dir):
        """
        Write the configuration file to the dest_dir.
        """
        generated_file_name = os.sep.join([generated_dir, self.name])

        puts('Generating {file_name}'.format(file_name=self.remote))

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
        local_file_name = os.sep.join([remotes_dir, self.name])

        puts('Pulling {file_name} from {host}'.format(file_name=self.remote,
                                                      host=options.get_hostname()))

        _ensure_dir(os.path.dirname(local_file_name))
        _clear_file(local_file_name)

        with settings(use_ssh_config=True):
            if exists(self.remote, use_sudo=options.use_sudo):
                get(self.remote, local_file_name)
            else:
                puts('Not found: {file_name}'.format(file_name=self.remote))

    def push(self, generated_dir):
        """
        Push the generated configuration file to the remote host.
        """
        generated_file_name = os.sep.join([generated_dir, self.name])
        remote_dir = os.path.dirname(self.remote)

        puts('Pushing {file_name} to {host}'.format(file_name=self.remote,
                                                    host=options.get_hostname()))

        with settings(use_ssh_config=True):
            mkdir_cmd = sudo if options.use_sudo else run
            mkdir_cmd('mkdir -p {dir_name}'.format(dir_name=remote_dir))

            put(generated_file_name,
                self.remote,
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
        host_generated_dir = os.sep.join([generated_dir, options.get_hostname()])

        _clear_dir(host_generated_dir)
        _ensure_dir(host_generated_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

    def pull(self, remotes_dir):
        """
        Pull remote versions of files into remotes_dir.
        """
        host_remotes_dir = os.sep.join([remotes_dir, options.get_hostname()])

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)

    def diff(self, generated_dir, remotes_dir):
        """
        Show diffs for all configuration files.
        """
        host_generated_dir = os.sep.join([generated_dir, options.get_hostname()])
        host_remotes_dir = os.sep.join([remotes_dir, options.get_hostname()])

        for conffile in self.conffiles:
            conffile.pull(host_remotes_dir)

        for conffile in self.conffiles:
            conffile.generate(host_generated_dir)

        for conffile in self.conffiles:
            conffile.diff(host_generated_dir, host_remotes_dir).show()

    def push(self, generated_dir, remotes_dir):
        """
        Push configuration files that have changes, given user confirmation.
        """
        host_generated_dir = os.sep.join([generated_dir, options.get_hostname()])
        host_remotes_dir = os.sep.join([remotes_dir, options.get_hostname()])

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
