"""
Determine the difference between remote and generated configuration files.
"""

from confab.conffiles import ConfFiles
from confab.data import DataLoader
from confab.loaders import FileSystemEnvironmentLoader
from confab.validate import validate_all

from fabric.api import task


@task
def diff(templates_dir=None,
         data_dir=None,
         generated_dir=None,
         remotes_dir=None):
    """
    Show configuration file diffs.
    """
    validate_all(templates_dir, data_dir, generated_dir, remotes_dir)

    conffiles = ConfFiles(FileSystemEnvironmentLoader(templates_dir),
                          DataLoader(data_dir))

    conffiles.diff(generated_dir, remotes_dir)
