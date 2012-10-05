"""
Generate configuration files into generated_dir.
"""

from files import get_conf_files, env_from_dir, _clear_dir, _ensure_dir
from fabric.api import abort, env, task
import os

def generate_conf_files(conf_files, generated_dir):
    """
    Write all configuration files to generated_dir.
    """
    _clear_dir(generated_dir)
    _ensure_dir(generated_dir)

    for conf_file in conf_files:
        conf_file.generate(generated_dir)


@task
def generate(template_dir=None, generated_dir=None):
    """
    Generate configuration files.
    """
    if not template_dir or not os.path.isdir(template_dir):
        abort('Please provide a valid template_dir')

    if not generated_dir or (os.path.exists(generated_dir) and not os.path.isdir(generated_dir)):
        abort('Please provide a valid generate_dir')

    if not env.host_string:
        abort('Please specify a host or a role')

    environment = env_from_dir(template_dir)
    conf_files = get_conf_files(environment)

    generate_conf_files(conf_files, generated_dir)
