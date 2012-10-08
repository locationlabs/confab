"""
Generate configuration files into generated_dir.
"""

from confab.conffiles import ConfFiles
from confab.data import load_data_from_dir
from confab.loaders import load_environment_from_dir
from confab.validate import validate_generate

from fabric.api import task

@task
def generate(templates_dir=None, data_dir=None, generated_dir=None):
    """
    Generate configuration files.
    """
    validate_generate(templates_dir, data_dir, generated_dir)

    conffiles = ConfFiles(load_environment_from_dir(templates_dir),
                          load_data_from_dir(data_dir))

    conffiles.generate(generated_dir)
