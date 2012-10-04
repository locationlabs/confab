"""
Pull configuration files from remote host into pull_dir.
"""

from files import get_conf_files, env_from_dir
from options import get_default_options
from fabric.api import abort, env, task
import os

def pull_conf_files(conf_files, pull_dir):
    """
    Pull remote versions of conf_files into pull_dir.
    """
    for conf_file in conf_files:
        local_file_name = os.sep.join([pull_dir,env.host_string,conf_file.name])
        conf_file.pull(local_file_name)

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

    options = get_default_options()
    jinja_env = env_from_dir(template_dir)
    data = {}
    conf_files = get_conf_files(jinja_env, data, options)

    pull_conf_files(conf_files, pull_dir)
