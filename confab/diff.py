"""
Determine the difference between remote and generated configuration files.
"""

from confab.conffiles import ConfFiles
from confab.data import load_data_from_dir
from confab.loaders import load_environment_from_dir
from confab.validate import validate_all

from fabric.api import task

@task
def diff(template_dir=None, data_dir=None, generated_dir=None, remotes_dir=None):
    """
    Show configuration file diffs.
    """
    validate_all(template_dir, data_dir, generated_dir, remotes_dir)

    conffiles = ConfFiles(load_environment_from_dir(template_dir),
                          load_data_from_dir(data_dir))

    conffiles.diff(generated_dir, remotes_dir)
