"""
Pull configuration files from remote host into remotes_dir.
"""

from confab.files import get_conf_files, env_from_dir
from confab.validate import validate_pull

from fabric.api import task
import os

def pull_conf_files(conf_files, remotes_dir):
    """
    Pull remote versions of conf_files into remotes_dir.
    """
    for conf_file in conf_files:
        conf_file.pull(remotes_dir)

@task
def pull(template_dir=None, remotes_dir=None):
    """
    Pull remote configuration files.
    """
    validate_pull(template_dir, remotes_dir)

    environment = env_from_dir(template_dir)
    conf_files = get_conf_files(environment)

    pull_conf_files(conf_files, remotes_dir)
