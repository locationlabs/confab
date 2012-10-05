"""
Determine the difference between remote and generated configuration files.
"""

from confab.data import get_configuration_data
from confab.conffiles import ConfFiles
from confab.loaders import load_from_dir
from confab.validate import validate_all

from fabric.api import task

@task
def diff(template_dir=None, data_dir=None, generated_dir=None, remotes_dir=None):
    """
    Show configuration file diffs.
    """
    validate_all(template_dir, data_dir, generated_dir, remotes_dir)

    conffiles = ConfFiles(load_from_dir(template_dir),
                          get_configuration_data(data_dir))

    conffiles.diff(generated_dir, remotes_dir)
