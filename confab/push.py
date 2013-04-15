"""
Push generated configuration files to remote host.
"""
from fabric.api import task
from gusset.output import status
from gusset.validation import with_validation

from confab.iter import iterconffiles


@task
@with_validation
def push(directory=None):
    """
    Push configuration files.
    """
    for conffiles in iterconffiles(directory):
        status("Pushing templates for '{environment}' and '{role}'",
               environment=conffiles.environment,
               role=conffiles.role)

        conffiles.push()
