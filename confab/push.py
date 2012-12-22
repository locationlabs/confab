"""
Push generated configuration files to remote host.
"""

from confab.conffiles import ConfFiles
from confab.data import load_data_from_dir
from confab.loaders import load_environment_from_dir
from confab.options import options, Options
from confab.validate import validate_all

from fabric.api import task


@task
def push(templates_dir=None,
         data_dir=None,
         generated_dir=None,
         remotes_dir=None,
         assume_yes=None):
    """
    Push configuration files.
    """
    validate_all(templates_dir, data_dir, generated_dir, remotes_dir)

    conffiles = ConfFiles(load_environment_from_dir(templates_dir),
                          load_data_from_dir(data_dir))

    assume_yes = options.assume_yes if assume_yes is None else assume_yes == 'True'

    with Options(assume_yes=assume_yes):
        conffiles.push(generated_dir, remotes_dir)
