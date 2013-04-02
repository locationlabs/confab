"""
Pull configuration files from remote host into remotes_dir.
"""

from confab.conffiles import ConfFiles
from confab.data import DataLoader
from confab.loaders import FileSystemEnvironmentLoader
from confab.validate import validate_pull

from fabric.api import task


@task
def pull(templates_dir=None, data_dir=None, remotes_dir=None):
    """
    Pull remote configuration files.
    """
    validate_pull(templates_dir, data_dir, remotes_dir)

    conffiles = ConfFiles(FileSystemEnvironmentLoader(templates_dir),
                          DataLoader(data_dir))

    conffiles.pull(remotes_dir)
