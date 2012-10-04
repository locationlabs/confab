"""
Push generated configuration files to remote host.
"""

from confab.files import get_conf_files, env_from_dir
from confab.generate import generate_conf_files
from confab.options import get_default_options
from fabric.api import abort, env, puts, task

import os

def push_conf_file(conf_file, generate_dir, options):
    pass

def push_conf_files(conf_files, generate_dir, options):

    # XXX prompt

    for conf_file in conf_files:
        push_conf_file(conf_file, generate_dir, options)

@task
def push(template_dir=None, generate_dir=None):
    """
    Push configuration files.
    """

    if not template_dir or not os.path.isdir(template_dir):
        abort('Please provide a valid template_dir')

    if not generate_dir or (os.path.exists(generate_dir) and not os.path.isdir(generate_dir)):
        abort('Please provide a valid generate_dir')

    if not env.host_string:
        abort('Please specify a host or a role')

    options = get_default_options()
    jinja_env = env_from_dir(template_dir)
    data = {}
    conf_files = get_conf_files(jinja_env, data, options)

    # Generate configuration files first
    generate_conf_files(conf_files, generate_dir, options)
    # Then push
    push_conf_files(conf_files, generate_dir, options)
