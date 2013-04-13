"""
Push generated configuration files to remote host.
"""
from fabric.api import abort, env, task
from gusset.output import status
from gusset.validation import with_validation

from confab.conffiles import iterconffiles


@task
@with_validation
def push(directory):
    """
    Push configuration files.
    """
    if 'environmentdef' not in env:
        abort("Confab needs to be configured")

    for conffiles in iterconffiles(env.environmentdef, directory):
        status("Pushing templates for '{environment}' and '{role}'",
               environment=env.environmentdef.name,
               role=conffiles.role)

        conffiles.push(directory)
