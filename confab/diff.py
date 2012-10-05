"""
Determine the difference between remote and generated configuration files.
"""

from confab.data import get_configuration_data
from confab.files import get_conf_files, env_from_dir
from confab.generate import generate_conf_files
from confab.options import options, Options
from confab.pull import pull_conf_files
from confab.validate import validate_all

from fabric.api import task
import os

def diff_conf_files(conf_files, generated_dir, remotes_dir):
    """
    Show diffs for all configuration files.
    """
    host_generated_dir = os.sep.join([generated_dir,options.get_hostname()])
    host_remotes_dir = os.sep.join([remotes_dir,options.get_hostname()])

    for conf_file in conf_files:
        conf_file.diff(host_generated_dir, host_remotes_dir, True)

@task
def diff(template_dir=None, data_dir=None, generated_dir=None, remotes_dir=None):
    """
    Show configuration file diffs.
    """
    validate_all(template_dir, data_dir, generated_dir, remotes_dir)
    environment = env_from_dir(template_dir)

    with Options(get_configuration_data = lambda: get_configuration_data(data_dir)):
        conf_files = get_conf_files(environment)

        pull_conf_files(conf_files, remotes_dir)
        generate_conf_files(conf_files, generated_dir)
        diff_conf_files(conf_files, generated_dir, remotes_dir)
