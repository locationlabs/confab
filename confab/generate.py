"""
Generate configuration files into generated_dir.
"""

from confab.files import get_conf_files, env_from_dir, _clear_dir, _ensure_dir
from confab.validate import validate_generate

from fabric.api import task
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
    validate_generate(template_dir, generated_dir)

    environment = env_from_dir(template_dir)
    conf_files = get_conf_files(environment)

    generate_conf_files(conf_files, generated_dir)
