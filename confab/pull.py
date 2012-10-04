"""
Pull configuration files from remote host into pull_dir.
"""

from files import get_conf_files, env_from_dir, _clear_file, _ensure_dir
from options import make_default_options
from fabric.api import abort, env, get, puts, settings, task
from fabric.contrib.files import exists
import os

def pull_conf_file(conf_file, pull_dir, options):
    """
    Pull remote version of conf_files into pull_dir.
    """
    remote_file_name = os.sep + conf_file.name
    local_file_name = os.sep.join([pull_dir,env.host_string,conf_file.name])

    _ensure_dir(os.path.dirname(local_file_name))
    _clear_file(local_file_name)

    puts('Getting {file_name} from {host}'.format(file_name=remote_file_name,
                                                  host=env.host_string))

    with settings(use_ssh_config = True):
        if exists(remote_file_name, use_sudo=options.use_sudo):
            get(remote_file_name, local_file_name)
        else:
            puts('Not found: {file_name}'.format(file_name=remote_file_name))


def pull_conf_files(conf_files, pull_dir, options):
    """
    Pull remote versions of conf_files into pull_dir.
    """
    for conf_file in conf_files:
        pull_conf_file(conf_file, pull_dir, options)


@task
def pull(template_dir=None, pull_dir=None):
    """
    Pull remote configuration files.
    """

    if not template_dir or not os.path.isdir(template_dir):
        abort('Please provide a valid template_dir')

    if not pull_dir or (os.path.exists(pull_dir) and not os.path.isdir(pull_dir)):
        abort('Please provide a valid pull_dir')

    if not env.host_string:
        abort('Please specify a host or a role')

    options = make_default_options()
    jinja_env = env_from_dir(template_dir)
    data = {}
    conf_files = get_conf_files(jinja_env, data, options)

    pull_conf_files(conf_files, pull_dir, options)
