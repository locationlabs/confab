"""
Push generated configuration files to remote host.
"""

from confab.data import get_configuration_data
from confab.conffiles import ConfFiles
from confab.loaders import load_from_dir
from confab.validate import validate_all

from fabric.api import task

@task
def push(template_dir=None, data_dir=None, generated_dir=None, remotes_dir=None):
    """
    Push configuration files.
    """
    validate_all(template_dir, data_dir, generated_dir, remotes_dir)

    conffiles = ConfFiles(load_from_dir(template_dir),
                          get_configuration_data(data_dir))

    conffiles.push(generated_dir, remotes_dir)
