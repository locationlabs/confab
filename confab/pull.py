"""
Pull configuration files from remote host into remotes_dir.
"""
from fabric.api import abort, env, task

from confab.conffiles import iterconffiles
from confab.output import status
from confab.validate import validate_pull


@task
def pull(templates_dir=None, data_dir=None, remotes_dir=None):
    """
    Pull remote configuration files.
    """
    validate_pull(templates_dir, data_dir, remotes_dir)

    if not env.confab:
        abort("Confab needs to be configured")

    for conffiles in iterconffiles(env.confab, templates_dir, data_dir):
        status("Pulling remote templates for '{environment}' and '{role}'",
               environment=env.confab.name,
               role=conffiles.role)

        conffiles.pull(remotes_dir)
