"""
Pull configuration files from remote host into remotes_dir.
"""

from confab.data import get_configuration_data
from confab.conffiles import ConfFiles
from confab.loaders import load_from_dir
from confab.validate import validate_pull

from fabric.api import task

@task
def pull(template_dir=None, data_dir=None, remotes_dir=None):
    """
    Pull remote configuration files.
    """
    validate_pull(template_dir, data_dir, remotes_dir)

    conffiles = ConfFiles(load_from_dir(template_dir),
                          get_configuration_data(data_dir))

    conffiles.pull(remotes_dir)
