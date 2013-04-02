"""
Generate configuration files into generated_dir.
"""

from confab.conffiles import ConfFiles
from confab.data import DataLoader
from confab.loaders import FileSystemEnvironmentLoader
from confab.validate import validate_generate

from fabric.api import task


@task
def generate(templates_dir=None, data_dir=None, generated_dir=None):
    """
    Generate configuration files.
    """
    validate_generate(templates_dir, data_dir, generated_dir)

    conffiles = ConfFiles(FileSystemEnvironmentLoader(templates_dir),
                          DataLoader(data_dir))

    conffiles.generate(generated_dir)
