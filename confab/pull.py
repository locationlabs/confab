"""
Pull configuration files from remote host into remotes_dir.
"""
from fabric.api import abort, env, task
from gusset.output import status
from gusset.validation import with_validation

from confab.conffiles import iterconffiles


@task
@with_validation
def pull(directory):
    """
    Pull remote configuration files.
    """
    if not env.confab:
        abort("Confab needs to be configured")

    for conffiles in iterconffiles(env.confab, directory):
        status("Pulling remote templates for '{environment}' and '{role}'",
               environment=env.confab.name,
               role=conffiles.role)

        conffiles.pull(directory)
