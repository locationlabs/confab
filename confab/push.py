"""
Push generated configuration files to remote host.
"""

from confab.data import get_configuration_data
from confab.files import get_conf_files, env_from_dir
from confab.generate import generate_conf_files
from confab.options import options, Options
from confab.pull import pull_conf_files
from confab.validate import validate_all

from fabric.api import task
from fabric.colors import magenta
from fabric.contrib.console import confirm

import os

def push_conf_files(conf_files, generated_dir, remotes_dir):
    """
    Push configuration files that have changes, given user confirmation.
    """
    host_generated_dir = os.sep.join([generated_dir,options.get_hostname()])
    host_remotes_dir = os.sep.join([remotes_dir,options.get_hostname()])

    has_diff = lambda conf_file: conf_file.diff(host_generated_dir, host_remotes_dir, True)
    with_diffs = filter(has_diff, conf_files)

    if not with_diffs:
        print(magenta('No configuration files to push for {host}'.format(host=options.get_hostname())))
        return

    print(magenta('The following configuration files have changed for {host}:'.format(host=options.get_hostname())))
    print
    for conf_file in with_diffs:
        print(magenta('\t' + conf_file.remote))

    if confirm('Push configuration files to {host}?'.format(host=options.get_hostname()),
               default=False):
        for conf_file in with_diffs:
            conf_file.push(host_generated_dir)

@task
def push(template_dir=None, data_dir=None, generated_dir=None, remotes_dir=None):
    """
    Push configuration files.
    """
    validate_all(template_dir, data_dir, generated_dir, remotes_dir)
    environment = env_from_dir(template_dir)

    with Options(get_configuration_data = lambda: get_configuration_data(data_dir)):
        conf_files = get_conf_files(environment)

        pull_conf_files(conf_files, remotes_dir)
        generate_conf_files(conf_files, generated_dir)
        push_conf_files(conf_files, generated_dir, remotes_dir)
