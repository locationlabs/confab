"""
Generate configuration files into generated_dir.
"""

from confab.data import get_configuration_data
from confab.files import get_conf_files, env_from_dir, _clear_dir, _ensure_dir
from confab.options import options, Options
from confab.validate import validate_generate

from fabric.api import task
import os

def generate_conf_files(conf_files, generated_dir):
    """
    Write all configuration files to generated_dir.
    """
    host_generated_dir = os.sep.join([generated_dir,options.get_hostname()])

    _clear_dir(host_generated_dir)
    _ensure_dir(host_generated_dir)

    for conf_file in conf_files:
        conf_file.generate(host_generated_dir)


@task
def generate(template_dir=None, data_dir=None, generated_dir=None):
    """
    Generate configuration files.
    """
    validate_generate(template_dir, data_dir, generated_dir)
    environment = env_from_dir(template_dir)

    with Options(get_configuration_data = lambda: get_configuration_data(data_dir)):
        conf_files = get_conf_files(environment)

        generate_conf_files(conf_files, generated_dir)
