"""
Generate configuration files into generate_dir.
"""

from files import get_conf_files, env_from_dir, _clear_dir, _ensure_dir
from options import get_default_options
from fabric.api import abort, env, task
import os

def generate_conf_files(conf_files, generate_dir):
    """
    Write all configuration files to generate_dir.
    """
    _clear_dir(generate_dir)
    _ensure_dir(generate_dir)

    for conf_file in conf_files:
        generated_file_name = os.sep.join([generate_dir,env.host_string,conf_file.name])
        conf_file.generate(generated_file_name)


@task
def generate(template_dir=None, generate_dir=None):
    """
    Generate configuration files.
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

    generate_conf_files(conf_files, generate_dir)
