"""
Pull configuration files from remote host into remotes_dir.
"""

from files import get_conf_files, env_from_dir
from fabric.api import abort, env, task
import os

def pull_conf_files(conf_files, remotes_dir):
    """
    Pull remote versions of conf_files into remotes_dir.
    """
    for conf_file in conf_files:
        conf_file.pull(remotes_dir)

@task
def pull(template_dir=None, remotes_dir=None):
    """
    Pull remote configuration files.
    """

    if not template_dir or not os.path.isdir(template_dir):
        abort('Please provide a valid template_dir')

    if not remotes_dir or (os.path.exists(remotes_dir) and not os.path.isdir(remotes_dir)):
        abort('Please provide a valid remotes_dir')

    if not env.host_string:
        abort('Please specify a host or a role')

    environment = env_from_dir(template_dir)
    conf_files = get_conf_files(environment)

    pull_conf_files(conf_files, remotes_dir)
