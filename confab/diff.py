"""
Determine the difference between remote and generated configuration files.
"""
from fabric.api import task
from gusset.output import status
from gusset.validation import with_validation

from confab.iter import iter_conffiles


@task
@with_validation
def diff(directory=None):
    """
    Show configuration file diffs.
    """
    for conffiles in iter_conffiles(directory):
        status("Computing template diffs for '{environment}' and '{role}'",
               environment=conffiles.environment,
               role=conffiles.role)

        conffiles.diff(directory)
