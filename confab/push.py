"""
Push generated configuration files to remote host.
"""

from confab.files import get_conf_files, env_from_dir
from confab.generate import generate_conf_files
from confab.pull import pull_conf_files
from confab.options import get_default_options
from fabric.api import abort, env, task
from fabric.colors import magenta
from fabric.contrib.console import confirm

import os

def push_conf_files(conf_files, generated_dir, remotes_dir):
    """
    Push configuration files that have changes, given user confirmation.
    """

    has_diff = lambda conf_file: conf_file.diff(generated_dir, remotes_dir, True)
    with_diffs = filter(has_diff, conf_files)

    if not with_diffs:
        print(magenta('No configuration files to push for {host}'.format(host=env.host_string)))
        return

    print(magenta('The following configuration files have changed for {host}:'.format(host=env.host_string)))
    print
    for conf_file in with_diffs:
        print(magenta('\t' + conf_file.remote))

    if confirm('Push configuration files to {host}?'.format(host=env.host_string),
               default=False):
        for conf_file in with_diffs:
            conf_file.push(generated_dir)

@task
def push(template_dir=None, generated_dir=None, remotes_dir=None):
    """
    Push configuration files.
    """

    if not template_dir or not os.path.isdir(template_dir):
        abort('Please provide a valid template_dir')

    if not generated_dir or (os.path.exists(generated_dir) and not os.path.isdir(generated_dir)):
        abort('Please provide a valid generated_dir')

    if not remotes_dir or (os.path.exists(remotes_dir) and not os.path.isdir(remotes_dir)):
        abort('Please provide a valid remotes_dir')

    if not env.host_string:
        abort('Please specify a host or a role')

    options = get_default_options()
    environment = env_from_dir(template_dir)
    data = {}
    conf_files = get_conf_files(environment, data, options)

    pull_conf_files(conf_files, remotes_dir)
    generate_conf_files(conf_files, generated_dir)
    push_conf_files(conf_files, generated_dir, remotes_dir)
