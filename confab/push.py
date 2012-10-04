"""
Push generated configuration files to remote host.
"""

from confab.files import get_conf_files, env_from_dir
from confab.generate import generate_conf_files
from confab.pull import pull_conf_files
from confab.options import get_default_options
from fabric.api import abort, env, task

import os

def push_conf_files(conf_files, generate_dir, pull_dir):

    # XXX diffs, defer push 

    for conf_file in conf_files:
        generated_file_name = os.sep.join([generate_dir,env.host_string,conf_file.name])
        local_file_name = os.sep.join([pull_dir,env.host_string,conf_file.name])

        conf_file.push(generated_file_name)

@task
def push(template_dir=None, generate_dir=None, pull_dir=None):
    """
    Push configuration files.
    """

    if not template_dir or not os.path.isdir(template_dir):
        abort('Please provide a valid template_dir')

    if not generate_dir or (os.path.exists(generate_dir) and not os.path.isdir(generate_dir)):
        abort('Please provide a valid generate_dir')

    if not pull_dir or (os.path.exists(pull_dir) and not os.path.isdir(pull_dir)):
        abort('Please provide a valid pull_dir')

    if not env.host_string:
        abort('Please specify a host or a role')

    options = get_default_options()
    jinja_env = env_from_dir(template_dir)
    data = {}
    conf_files = get_conf_files(jinja_env, data, options)

    pull_conf_files(conf_files, pull_dir)
    generate_conf_files(conf_files, generate_dir)
    push_conf_files(conf_files, generate_dir, pull_dir)
