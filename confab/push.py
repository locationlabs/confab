"""
Push generated configuration files to remote host.
"""
from fabric.api import task
from gusset.output import status
from gusset.validation import with_validation

from confab.iter import iter_conffiles


@task
@with_validation
def push(directory=None):
    """
    Push configuration files.
    """
    for conffiles in iter_conffiles(directory):
        status("Pushing templates for '{environment}' and '{role}'",
               environment=conffiles.environment,
               role=conffiles.role)

        conffiles.push()
